import algoliasearch from 'algoliasearch/lite'
import React, { useContext } from 'react'
import { Configure, InstantSearch } from 'react-instantsearch-dom'

import { AuthenticatedResponse, VenueResponse } from 'apiClient/adage'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'

import { FacetFiltersContext } from '../../providers'
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
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}

const OffersForMyInstitution = ({
  user,
  venueFilter,
  removeVenueFilter,
}: OffersForMyInstitutionProps): JSX.Element => {
  const { facetFilters } = useContext(FacetFiltersContext)

  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
    >
      <Configure
        attributesToHighlight={[]}
        attributesToRetrieve={attributesToRetrieve}
        clickAnalytics
        facetFilters={facetFilters}
        hitsPerPage={8}
      />
      <AnalyticsContextProvider>
        <OffersInstitutionList
          removeVenueFilter={removeVenueFilter}
          user={user}
          venueFilter={venueFilter}
        />
      </AnalyticsContextProvider>
    </InstantSearch>
  )
}

export default OffersForMyInstitution
