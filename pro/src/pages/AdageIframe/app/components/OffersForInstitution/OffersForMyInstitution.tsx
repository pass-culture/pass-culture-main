import algoliasearch from 'algoliasearch/lite'
import React from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { VenueResponse } from 'apiClient/adage'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import useAdageUser from '../../hooks/useAdageUser'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'

import OffersInstitutionList from './OffersInstitutionList/OffersInstitutionList'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)
const attributesToRetrieve = [
  'objectID',
  'offer.dates',
  'offer.name',
  'offer.thumbUrl',
  'venue.name',
  'venue.publicName',
  'isTemplate',
  'offer.interventionArea',
]
interface OffersForMyInstitutionProps {
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}

const OffersForMyInstitution = ({
  venueFilter,
  removeVenueFilter,
}: OffersForMyInstitutionProps): JSX.Element => {
  const adageUser = useAdageUser()
  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
        clickAnalytics
        facetFilters={[`offer.educationalInstitutionUAICode:${adageUser.uai}`]}
        hitsPerPage={8}
      />
      <AnalyticsContextProvider>
        <OffersInstitutionList
          removeVenueFilter={removeVenueFilter}
          venueFilter={venueFilter}
        />
      </AnalyticsContextProvider>
    </InstantSearch>
  )
}

export default OffersForMyInstitution
