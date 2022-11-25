from requests import Session
from selectolax.parser import HTMLParser
from datetime import datetime
import pytz
from pprint import PrettyPrinter #Not Necessary

def __scrape_json__():
    QUERY = """query OffersContext_Offers($dateOverride: Time) {
        primeOffers(dateOverride: $dateOverride) {
                ...PrimeOffer
                __typename
            }
        }
    
        fragment PrimeOfferAssets_Pixels on PrimeOfferAssets {
            id
            pixels {
                ...Pixel
                __typename
                }
            __typename
        }
    
        fragment PrimeOffer on PrimeOffer {
            catalogId
            id
            title
            assets {
                type
                purpose
                location
                location2x
                __typename
            }
            offerAssets {
                ...PrimeOfferAssets_Pixels
                __typename
            }
            description
            deliveryMethod
            isRetailLinkOffer
            priority
            tags {
                type
                tag
                __typename
            }
            content {
                externalURL
                publisher
                categories
                __typename
            }
            startTime
            endTime
            self {
                claimInstructions
                orderInformation {
                    ...PrimeOfferOrderInformation
                    __typename
                }
                eligibility {
                    ...PrimeOfferEligibility
                    __typename
                }
                __typename
            }
            linkedJourney {
                ...LinkedJourney
                __typename
            }
            __typename
        }
    
        fragment PrimeOfferEligibility on OfferEligibility {
            isClaimed
            canClaim
            isPrimeGaming
            missingRequiredAccountLink
            offerStartTime
            offerEndTime
            offerState
            gameAccountDisplayName
            inRestrictedMarketplace
            maxOrdersExceeded
            conflictingClaimAccount {
                ...ConflictingClaimAccount
                __typename
            }
            __typename
        }
    
        fragment LinkedJourney on Journey {
            offers {
                ...LinkedJourneyOffer
                __typename
            }
            __typename
        }
    
        fragment LinkedJourneyOffer on JourneyOffer {
            catalogId
            grantsCode
            self {
                eligibility(getOnlyActiveOffers: true) {
                    canClaim
                    isClaimed
                    conflictingClaimAccount {
                            ...ConflictingClaimAccount
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
                __typename
        }
    
        fragment PrimeOfferOrderInformation on OfferOrderInformation {
            orderDate
            orderState
            claimCode
            __typename
        }
    
        fragment Pixel on Pixel {
            type
            pixel
            __typename
        }
    
        fragment ConflictingClaimAccount on ConflictingClaimUser {
            fullName
            obfuscatedEmail
            __typename
        }
    """
    session = Session()
    session.headers["User-Agent"] = 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'

    # get_crfs_token started here
    res = session.get("https://gaming.amazon.com/home")
    res.raise_for_status()
    text = res.text
    tree = HTMLParser(text)
    csrf_token = str(tree.css_first("input[name=csrf-key]").attributes["value"])
    # grab offers started here
    res = session.post(
        'https://gaming.amazon.com/graphql',
        headers={
            "csrf-token": csrf_token,
        },
        json={
            "operationName": "OffersContext_Offers",
            "variables": {},
            "query": QUERY,
            "extensions": {}
        }
    )
    res.raise_for_status()

    offers = res.json()["data"]["primeOffers"]
    offers = filter(lambda offer: "Games with Prime" in offer["content"]["categories"], offers)
    raw = list(offers)
    return raw


def __format__(raw_json):
    """Formats and converts Scraped data into a dict"""
    games = {}
    raw = raw_json
    for i in range(len(raw)):  # Formats raw json into a dictionary
        title = raw[i]['title']
        url = raw[i]['content']['externalURL']
        external = True
        if not url:
            url = "https://gaming.amazon.com/home"
            external = False
        image = raw[i]['assets'][0]['location']
        publisher = raw[i]['content']['publisher']
        startTime = datetime(int(raw[i]['startTime'][0:4]),  # year
                             int(raw[i]['startTime'][5:7]),  # month
                             int(raw[i]['startTime'][8:10]),  # day
                             int(raw[i]['startTime'][11:13]),  # hour
                             int(raw[i]['startTime'][14:16]),  # minute
                             int(raw[i]['startTime'][17:19]),  # second
                             tzinfo=pytz.UTC)
        endTime = datetime(int(raw[i]['endTime'][0:4]),  # year
                           int(raw[i]['endTime'][5:7]),  # month
                           int(raw[i]['endTime'][8:10]),  # day
                           int(raw[i]['endTime'][11:13]),  # hour
                           int(raw[i]['endTime'][14:16]),  # minute
                           int(raw[i]['endTime'][17:19]),  # second
                           tzinfo=pytz.UTC)
        games[title] = {'url': url, 'image': image, 'publisher': publisher, 'startTime': startTime,
                        'endTime': endTime, 'external':external}
    return games


def ScrapeFGWP():
    """prints and returns dictionary of available games"""
    games = __format__(__scrape_json__())
    p = PrettyPrinter(indent=1)
    p.pprint(games)
    return games
