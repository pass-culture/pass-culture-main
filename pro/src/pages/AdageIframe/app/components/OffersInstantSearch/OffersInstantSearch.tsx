import algoliasearch from 'algoliasearch/lite'
import React, { useEffect, useState } from 'react'
import { Configure, Index, InstantSearch } from 'react-instantsearch'

import { VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'
import { getDefaultFacetFilterUAICodeValue } from 'utils/facetFilters'
import { isNumber } from 'utils/types'

import useAdageUser from '../../hooks/useAdageUser'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'
import { Facets } from '../../types'

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

export const OffersInstantSearch = (): JSX.Element => {
  const { adageUser } = useAdageUser()

  const params = new URLSearchParams(window.location.search)
  const venueId = Number(params.get('venue'))
  const siret = params.get('siret')
  const domainId = params.get('domain')
  const relativeOffersIncluded = params.get('all') === 'true'

  const [facetFilters, setFacetFilters] = useState<Facets>([
    ...getDefaultFacetFilterUAICodeValue(adageUser?.uai),
  ])

  const [geoRadius, setGeoRadius] = useState<number>(DEFAULT_GEO_RADIUS)

  const [venueFilter, setVenueFilter] = useState<VenueResponse | null>(null)
  const [loadingVenue, setLoadingVenue] = useState<boolean>(false)

  const notification = useNotification()

  useEffect(() => {
    async function setVenueFromUrl() {
      setLoadingVenue(true)
      if (!siret && !venueId) {
        return
      }

      try {
        const result = siret
          ? await apiAdage.getVenueBySiret(siret, relativeOffersIncluded)
          : await apiAdage.getVenueById(venueId, relativeOffersIncluded)

        setVenueFilter(result)

        setFacetFilters((prev) => [...prev, [`venue.id:${venueId}`]])
      } catch {
        notification.error('Lieu inconnu. Tous les résultats sont affichés.')
      } finally {
        setLoadingVenue(false)
      }
    }

    if (siret || venueId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setVenueFromUrl()
    }

    if (domainId) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setFacetFilters((prev) => [...prev, [`offer.domains:${domainId}`]])
    }
  }, [venueId, siret, domainId, relativeOffersIncluded, notification])

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
        {loadingVenue ? (
          <Spinner />
        ) : (
          <AnalyticsContextProvider>
            <OffersSearch
              setFacetFilters={setFacetFilters}
              venueFilter={venueFilter}
              domainsFilter={domainId}
              setGeoRadius={setGeoRadius}
            />
          </AnalyticsContextProvider>
        )}
      </Index>
    </InstantSearch>
  )
}
