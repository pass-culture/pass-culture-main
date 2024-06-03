import AlgoliaSearchInsights from 'search-insights'

import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

export const initAlgoliaAnalytics = (uniqueId: string) => {
  AlgoliaSearchInsights('init', {
    appId: ALGOLIA_APP_ID,
    apiKey: ALGOLIA_API_KEY,
    userToken: uniqueId,
  })
}

export const logOfferConversion = (objectID: string, queryID: string) => {
  AlgoliaSearchInsights('convertedObjectIDsAfterSearch', {
    eventName: 'Offer booked on adage',
    index: ALGOLIA_COLLECTIVE_OFFERS_INDEX,
    queryID,
    objectIDs: [objectID],
  })
}

export const logClickOnOffer = (
  objectID: string,
  position: number,
  queryID: string
) => {
  AlgoliaSearchInsights('clickedObjectIDsAfterSearch', {
    eventName: 'Offer clicked on adage',
    index: ALGOLIA_COLLECTIVE_OFFERS_INDEX,
    queryID,
    objectIDs: [objectID],
    // for Algolia, position start at 1 instead of 0
    positions: [position + 1],
  })
}
