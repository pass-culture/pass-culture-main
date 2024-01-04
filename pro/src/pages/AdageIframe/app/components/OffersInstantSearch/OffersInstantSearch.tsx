import algoliasearch from 'algoliasearch/lite'
import React, { useContext, useEffect, useState } from 'react'
import { Configure, Index, InstantSearch } from 'react-instantsearch'
import { useParams } from 'react-router-dom'

import { VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'
import { isNumber } from 'utils/types'

import useAdageUser from '../../hooks/useAdageUser'
import { FacetFiltersContext } from '../../providers'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'

import { OffersSearch } from './OffersSearch/OffersSearch'

const searchClient = algoliasearch(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

export const MAIN_INDEX_ID = 'main_offers_index'

export const algoliaSearchDefaultAttributesToRetrieve = [
  'objectID',
  'offer.dates',
  'offer.name',
  'offer.thumbUrl',
  'venue.name',
  'venue.publicName',
  'isTemplate',
  'offer.interventionArea',
]

export const DEFAULT_GEO_RADIUS = 30000000 // 30 000 km ensure we get all results in the world

export const OffersInstantSearch = ({
  venueFilter,
}: {
  venueFilter: VenueResponse | null
}): JSX.Element => {
  const { facetFilters, setFacetFilters } = useContext(FacetFiltersContext)

  const [geoRadius, setGeoRadius] = useState<number>(DEFAULT_GEO_RADIUS)
  const { adageUser } = useAdageUser()
  const { venueId } = useParams<{
    venueId: string
  }>()

  const [venueFilterFromParam, setVenueFilterFromParam] =
    useState<VenueResponse | null>(null)

  const notification = useNotification()

  useEffect(() => {
    const getVenueById = async () => {
      try {
        const venueResponse = await apiAdage.getVenueById(Number(venueId))
        setVenueFilterFromParam(venueResponse)
        setFacetFilters([...facetFilters, [`venue.id:${venueId}`]])
      } catch {
        notification.error('Lieu inconnu. Tous les résultats sont affichés.')
      }
    }
    if (venueId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      getVenueById()
    }
  }, [venueId])

  return (
    <InstantSearch
      indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
      searchClient={searchClient}
      future={{ preserveSharedStateOnUnmount: true }} // InstantSearch recommendation to prepare for version 8
    >
      <Index
        indexName={ALGOLIA_COLLECTIVE_OFFERS_INDEX}
        indexId={MAIN_INDEX_ID}
      >
        <Configure
          attributesToHighlight={[]}
          attributesToRetrieve={algoliaSearchDefaultAttributesToRetrieve}
          clickAnalytics
          facetFilters={facetFilters}
          filters={
            'offer.eventAddressType:offererVenue<score=3> OR offer.eventAddressType:school<score=2> OR offer.eventAddressType:other<score=1>'
          }
          hitsPerPage={8}
          aroundLatLng={
            isNumber(adageUser.lat) && isNumber(adageUser.lon)
              ? `${adageUser.lat}, ${adageUser.lon}`
              : undefined
          }
          aroundRadius={geoRadius}
          distinct={false}
        />
        <AnalyticsContextProvider>
          <OffersSearch
            venueFilter={venueFilter || venueFilterFromParam}
            setGeoRadius={setGeoRadius}
          />
        </AnalyticsContextProvider>
      </Index>
    </InstantSearch>
  )
}
