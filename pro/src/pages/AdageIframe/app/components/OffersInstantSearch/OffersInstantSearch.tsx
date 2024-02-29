import algoliasearch from 'algoliasearch/lite'
import React, { useEffect, useState } from 'react'
import { Configure, Index, InstantSearch } from 'react-instantsearch'

import { VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { StudentLevels } from 'apiClient/v1'
import useActiveFeature from 'hooks/useActiveFeature'
import useNotification from 'hooks/useNotification'
import Spinner from 'ui-kit/Spinner/Spinner'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'
import { isNumber } from 'utils/types'

import { MARSEILLE_EN_GRAND } from '../../constants'
import useAdageUser from '../../hooks/useAdageUser'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'
import { Facets } from '../../types'

import { OffersSearch } from './OffersSearch/OffersSearch'
import {
  ADAGE_FILTERS_DEFAULT_VALUES,
  adageFiltersToFacetFilters,
} from './utils'

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

const DEFAULT_MARSEILLE_STUDENTS = [
  StudentLevels._COLES_MARSEILLE_MATERNELLE,
  StudentLevels._COLES_MARSEILLE_CP_CE1_CE2,
  StudentLevels._COLES_MARSEILLE_CM1_CM2,
]

export const OffersInstantSearch = (): JSX.Element | null => {
  const { adageUser } = useAdageUser()

  const params = new URLSearchParams(window.location.search)
  const venueParam = Number(params.get('venue'))
  const siretParam = params.get('siret')
  const domainParam = Number(params.get('domain'))
  const relativeOffersIncludedParam = params.get('all') === 'true'
  const programParam = params.get('program')

  const isMarseilleEnabled = useActiveFeature('WIP_ENABLE_MARSEILLE')
  const isUserInMarseilleProgram = (adageUser.programs ?? []).some(
    (prog) => prog.name === MARSEILLE_EN_GRAND
  )
  const filterOnMarseilleStudents =
    isMarseilleEnabled && isUserInMarseilleProgram && programParam

  const [facetFilters, setFacetFilters] = useState<Facets | null>(null)

  const [geoRadius, setGeoRadius] = useState<number>(DEFAULT_GEO_RADIUS)

  const [venueFilter, setVenueFilter] = useState<VenueResponse | null>(null)
  const [loadingVenue, setLoadingVenue] = useState<boolean>(false)

  const notification = useNotification()

  useEffect(() => {
    function setFacetFiltersFromParams(venue?: VenueResponse | null) {
      const filtersFromParams = {
        uai: adageUser?.uai ? [adageUser.uai, 'all'] : ['all'],
        domains: domainParam ? [domainParam] : [],
        students: filterOnMarseilleStudents ? DEFAULT_MARSEILLE_STUDENTS : [],
        venue: venue ?? null,
      }
      setFacetFilters(
        adageFiltersToFacetFilters({
          ...ADAGE_FILTERS_DEFAULT_VALUES,
          ...filtersFromParams,
        }).queryFilters
      )
    }

    async function setVenueFromUrl() {
      if (!siretParam && !venueParam) {
        return
      }

      setLoadingVenue(true)

      try {
        const result = siretParam
          ? await apiAdage.getVenueBySiret(
              siretParam,
              relativeOffersIncludedParam
            )
          : await apiAdage.getVenueById(venueParam, relativeOffersIncludedParam)

        setVenueFilter(result)
        setFacetFiltersFromParams(result)
      } catch {
        notification.error('Lieu inconnu. Tous les résultats sont affichés.')
        setFacetFiltersFromParams()
      } finally {
        setLoadingVenue(false)
      }
    }

    if (siretParam || venueParam) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setVenueFromUrl()
    } else {
      //  If a venue has to be fetched, the params will be set when that's done. Otherwise, we can set the filters directy.
      setFacetFiltersFromParams()
    }
  }, [
    venueParam,
    siretParam,
    relativeOffersIncludedParam,
    notification,
    adageUser,
    domainParam,
    filterOnMarseilleStudents,
  ])

  return loadingVenue ? (
    <Spinner />
  ) : facetFilters ? (
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
            setFacetFilters={setFacetFilters}
            initialFilters={{
              venue: venueFilter,
              domains: domainParam ? [domainParam] : [],
              students: filterOnMarseilleStudents
                ? DEFAULT_MARSEILLE_STUDENTS
                : [],
            }}
            setGeoRadius={setGeoRadius}
          />
        </AnalyticsContextProvider>
      </Index>
    </InstantSearch>
  ) : null
}
