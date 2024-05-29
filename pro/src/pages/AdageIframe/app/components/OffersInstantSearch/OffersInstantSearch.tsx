import algoliasearch from 'algoliasearch/lite'
import { useEffect, useState } from 'react'
import { Configure, Index, InstantSearch } from 'react-instantsearch'
import { useSelector } from 'react-redux'

import { VenueResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { DEFAULT_MARSEILLE_STUDENTS } from 'core/shared/constants'
import useActiveFeature from 'hooks/useActiveFeature'
import { useNotification } from 'hooks/useNotification'
import { adageFilterSelector } from 'store/adageFilter/selectors'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import {
  ALGOLIA_API_KEY,
  ALGOLIA_APP_ID,
  ALGOLIA_COLLECTIVE_OFFERS_INDEX,
} from 'utils/config'
import { isNumber } from 'utils/types'

import { MARSEILLE_EN_GRAND } from '../../constants'
import { useAdageUser } from '../../hooks/useAdageUser'
import { AnalyticsContextProvider } from '../../providers/AnalyticsContextProvider'

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

export interface SearchFormValues {
  domains: number[]
  students: string[]
  departments: string[]
  academies: string[]
  eventAddressType: string
  geolocRadius: number
  formats: string[]
  venue: VenueResponse | null
}

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

  const adageFilterFromSelector = useSelector(adageFilterSelector)

  const notification = useNotification()

  const filterOnMarseilleStudents =
    isMarseilleEnabled && isUserInMarseilleProgram && programParam

  const [geoRadius, setGeoRadius] = useState<number>(
    adageFilterFromSelector.geolocRadius ===
      ADAGE_FILTERS_DEFAULT_VALUES.geolocRadius
      ? DEFAULT_GEO_RADIUS
      : adageFilterFromSelector.geolocRadius * 1000
  )

  const [isLoadingVenue, setIsLoadingVenue] = useState(Boolean(venueParam))

  const hasQueryParams = venueParam || domainParam || filterOnMarseilleStudents

  const filtersFromParams = {
    ...ADAGE_FILTERS_DEFAULT_VALUES,
    domains: domainParam ? [domainParam] : adageFilterFromSelector.domains,
    students:
      adageFilterFromSelector.students.length > 0
        ? adageFilterFromSelector.students
        : filterOnMarseilleStudents
          ? DEFAULT_MARSEILLE_STUDENTS
          : [],
    venue: adageFilterFromSelector.venue,
  }

  const [filters, setFilters] = useState<SearchFormValues>(
    hasQueryParams ? filtersFromParams : adageFilterFromSelector
  )

  useEffect(() => {
    async function setVenueFromUrl() {
      if (!siretParam && !venueParam) {
        return
      }

      setIsLoadingVenue(true)

      try {
        const result = siretParam
          ? await apiAdage.getVenueBySiret(
              siretParam,
              relativeOffersIncludedParam
            )
          : await apiAdage.getVenueById(venueParam, relativeOffersIncludedParam)

        setFilters({ ...ADAGE_FILTERS_DEFAULT_VALUES, venue: result })
      } catch {
        notification.error('Lieu inconnu. Tous les résultats sont affichés.')
      } finally {
        setIsLoadingVenue(false)
      }
    }

    if (siretParam || venueParam) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      setVenueFromUrl()
    }
  }, [venueParam, siretParam, relativeOffersIncludedParam, notification])

  if (isLoadingVenue) {
    return <Spinner />
  }

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
          facetFilters={
            adageFiltersToFacetFilters({
              ...filters,
              uai: adageUser.uai ? ['all', adageUser.uai] : ['all'],
            }).queryFilters
          }
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
            setFilters={setFilters}
            initialFilters={filters}
            setGeoRadius={setGeoRadius}
          />
        </AnalyticsContextProvider>
      </Index>
    </InstantSearch>
  )
}
