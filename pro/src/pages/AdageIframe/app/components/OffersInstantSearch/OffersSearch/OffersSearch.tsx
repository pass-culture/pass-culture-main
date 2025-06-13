import { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react'
import { FormProvider, useForm } from 'react-hook-form'
import { useInstantSearch } from 'react-instantsearch'
import { useDispatch, useSelector } from 'react-redux'
import { useSearchParams } from 'react-router'
import useSWRMutation from 'swr/mutation'

import { AdageFrontRoles, TrackingFilterBody } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { LOG_TRACKING_FILTER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { GET_DATA_ERROR_MESSAGE } from 'commons/core/shared/constants'
import { useEducationalDomains } from 'commons/hooks/swr/useEducationalDomains'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useIsElementVisible } from 'commons/hooks/useIsElementVisible'
import { useNotification } from 'commons/hooks/useNotification'
import {
  setAdageFilter,
  setAdagePageSaved,
} from 'commons/store/adageFilter/reducer'
import { adageQuerySelector } from 'commons/store/adageFilter/selectors'
import { MARSEILLE_EN_GRAND } from 'pages/AdageIframe/app/constants'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'

import {
  DEFAULT_GEO_RADIUS,
  MAIN_INDEX_ID,
  SearchFormValues,
} from '../OffersInstantSearch'
import { ADAGE_FILTERS_DEFAULT_VALUES, serializeFiltersForData } from '../utils'

import { Autocomplete } from './Autocomplete/Autocomplete'
import { FiltersTags } from './FiltersTags/FiltersTags'
import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import styles from './OffersSearch.module.scss'
import { OffersSuggestions } from './OffersSuggestions/OffersSuggestions'

export enum LocalisationFilterStates {
  DEPARTMENTS = 'departments',
  ACADEMIES = 'academies',
  GEOLOCATION = 'geolocation',
  NONE = 'none',
}

export interface SearchProps {
  setFilters: Dispatch<SetStateAction<SearchFormValues>>
  initialFilters: Partial<SearchFormValues>
  setGeoRadius: (geoRadius: number) => void
}

export const OffersSearch = ({
  setFilters,
  setGeoRadius,
  initialFilters,
}: SearchProps): JSX.Element => {
  const dispatch = useDispatch()

  const [searchParams, setSearchParams] = useSearchParams()

  const { adageUser } = useAdageUser()
  const isUserAdmin = adageUser.role === AdageFrontRoles.READONLY

  const notification = useNotification()
  const adageQueryFromSelector = useSelector(adageQuerySelector)

  const { scopedResults } = useInstantSearch()

  const mainOffersSearchResults = scopedResults.find(
    (res) => res.indexId === MAIN_INDEX_ID
  )?.results
  const nbHits = mainOffersSearchResults?.nbHits

  useEffect(() => {
    if (mainOffersSearchResults) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      logFiltersOnSearch(
        mainOffersSearchResults.nbHits,
        mainOffersSearchResults.queryID
      )
    }
  }, [mainOffersSearchResults?.queryID])

  const isMarseilleEnabled = useActiveFeature('ENABLE_MARSEILLE')
  const isUserInMarseilleProgram = (adageUser.programs ?? []).some(
    (prog) => prog.name === MARSEILLE_EN_GRAND
  )

  const form = useForm<SearchFormValues>({
    defaultValues: { ...ADAGE_FILTERS_DEFAULT_VALUES, ...initialFilters },
  })

  const { trigger: logTrackingFilter } = useSWRMutation(
    LOG_TRACKING_FILTER_QUERY_KEY,
    (
      _key: string,
      options: {
        arg: TrackingFilterBody
      }
    ) => apiAdage.logTrackingFilter(options.arg)
  )

  const { data: educationalDomains, error: educationalDomainsApiError } =
    useEducationalDomains()

  if (educationalDomainsApiError) {
    notification.error(GET_DATA_ERROR_MESSAGE)
  }

  const domainsOptions = educationalDomains.map(({ id, name }) => ({
    value: id,
    label: name,
  }))

  function onSubmit() {
    resetUrlSearchFilterParams()
    dispatch(setAdageFilter(form.watch()))
    dispatch(setAdagePageSaved(0))
    setFilters(form.watch())

    const adageUserHasValidGeoloc =
      (adageUser.lat || adageUser.lat === 0) &&
      (adageUser.lon || adageUser.lon === 0)
    if (adageUserHasValidGeoloc) {
      setGeoRadius(
        localisationFilterState === LocalisationFilterStates.GEOLOCATION
          ? form.watch('geolocRadius') * 1000
          : DEFAULT_GEO_RADIUS
      )
    }
  }

  function resetUrlSearchFilterParams() {
    searchParams.delete('domain')
    searchParams.delete('venue')
    searchParams.delete('siret')
    searchParams.delete('program')
    searchParams.delete('all')
    setSearchParams(searchParams)
  }

  const resetForm = () => {
    setlocalisationFilterState(LocalisationFilterStates.NONE)
    Object.entries(ADAGE_FILTERS_DEFAULT_VALUES).map(([key, value]) => {
      form.setValue(key as keyof SearchFormValues, value)
    })
    onSubmit()
  }

  async function logFiltersOnSearch(nbHits: number, queryId?: string) {
    /* istanbul ignore next: TO FIX the current structure make it hard to test, we probably should not mock Offers in OfferSearch tests */
    if (form.formState.submitCount > 0 || adageQueryFromSelector !== null) {
      await logTrackingFilter({
        iframeFrom: location.pathname,
        resultNumber: nbHits,
        queryId: queryId ?? null,
        filterValues: serializeFiltersForData(
          form.watch(),
          adageQueryFromSelector,
          domainsOptions
        ),
      })
    }
  }

  const getActiveLocalisationFilter = () => {
    if (form.watch('departments').length > 0) {
      return LocalisationFilterStates.DEPARTMENTS
    }
    if (form.watch('academies').length > 0) {
      return LocalisationFilterStates.ACADEMIES
    }
    if (
      form.watch('geolocRadius') !== ADAGE_FILTERS_DEFAULT_VALUES.geolocRadius
    ) {
      return LocalisationFilterStates.GEOLOCATION
    }
    return LocalisationFilterStates.NONE
  }
  const [localisationFilterState, setlocalisationFilterState] =
    useState<LocalisationFilterStates>(getActiveLocalisationFilter())

  const offerFilterRef = useRef<HTMLDivElement>(null)
  const [isOfferFiltersVisible] = useIsElementVisible(offerFilterRef)
  return (
    <>
      <FormProvider {...form}>
        <Autocomplete
          initialQuery={adageQueryFromSelector ?? ''}
          handleSubmit={onSubmit}
        />
        <div className={styles['separator']} />
        <div ref={offerFilterRef}>
          <OfferFilters
            className={styles['search-filters']}
            localisationFilterState={localisationFilterState}
            setLocalisationFilterState={setlocalisationFilterState}
            domainsOptions={domainsOptions}
            shouldDisplayMarseilleStudentOptions={
              isMarseilleEnabled && isUserInMarseilleProgram
            }
          />
        </div>

        <FiltersTags
          domainsOptions={domainsOptions}
          localisationFilterState={localisationFilterState}
          setLocalisationFilterState={setlocalisationFilterState}
          resetForm={resetForm}
        />
      </FormProvider>
      <div className="search-results">
        <Offers
          submitCount={form.formState.submitCount}
          isBackToTopVisibile={!isOfferFiltersVisible}
          indexId={MAIN_INDEX_ID}
          venue={form.watch('venue')}
        />
        {nbHits === 0 && !isUserAdmin && (
          <OffersSuggestions formValues={form.watch()} />
        )}
      </div>
    </>
  )
}
