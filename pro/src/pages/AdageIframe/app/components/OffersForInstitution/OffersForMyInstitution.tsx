import algoliasearch from 'algoliasearch/lite'
import React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch'

import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import useAdageUser from '../../hooks/useAdageUser'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'
import { algoliaSearchDefaultAttributesToRetrieve } from '../OffersInstantSearch/OffersInstantSearch'
import { Offers } from '../OffersInstantSearch/OffersSearch/Offers/Offers'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

const OffersForMyInstitution = (): JSX.Element => {
  const { adageUser } = useAdageUser()
  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={algoliaSearchDefaultAttributesToRetrieve}
        clickAnalytics
        facetFilters={[`offer.educationalInstitutionUAICode:${adageUser.uai}`]}
        hitsPerPage={8}
        distinct={false}
      />
      <AnalyticsContextProvider>
        <Offers displayStats={false} />
      </AnalyticsContextProvider>
    </InstantSearch>
  )
}

export default OffersForMyInstitution
