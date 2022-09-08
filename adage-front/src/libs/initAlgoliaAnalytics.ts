import AlgoliaSearchInsights from 'search-insights'
import { v1 as uuid } from 'uuid'

import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

export const initAlgoliaAnalytics = () => {
  AlgoliaSearchInsights('init', {
    appId: ALGOLIA_APP_ID,
    apiKey: ALGOLIA_API_KEY,
    userToken: uuid(),
  })
}

export const logOfferConversion = async (objectID: string, queryID: string) => {
  if (queryID === undefined) {
    return
  }

  AlgoliaSearchInsights('convertedObjectIDsAfterSearch', {
    eventName: 'Offer booked on adage',
    index: ALGOLIA_COLLECTIVE_OFFERS_INDEX,
    queryID: queryID,
    objectIDs: [objectID],
  })
}

export const logClickOnOffer = async (
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
