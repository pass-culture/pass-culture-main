import { FormikContext, useFormik } from 'formik'
import { useContext, useEffect, useRef, useState } from 'react'

import { VenueResponse } from 'apiClient/adage'
import { api, apiAdage } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import useIsElementVisible from 'hooks/useIsElementVisible'
import useNotification from 'hooks/useNotification'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { FacetFiltersContext } from 'pages/AdageIframe/app/providers'
import { Option } from 'pages/AdageIframe/app/types'
import { filterEducationalSubCategories } from 'utils/collectiveCategories'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import {
  ADAGE_FILTERS_DEFAULT_VALUES,
  adageFiltersToFacetFilters,
  computeFiltersInitialValues,
  serializeFiltersForData,
} from '../utils'

import { Autocomplete } from './Autocomplete/Autocomplete'
import { OfferFilters } from './OfferFilters/OfferFilters'
import { Offers } from './Offers/Offers'
import styles from './OffersSearch.module.scss'

export enum LocalisationFilterStates {
  DEPARTMENTS = 'departments',
  ACADEMIES = 'academies',
  GEOLOCATION = 'geolocation',
  NONE = 'none',
}

export interface SearchProps {
  venueFilter: VenueResponse | null
  setGeoRadius: (geoRadius: number | null) => void
}

export interface SearchFormValues {
  domains: string[]
  students: string[]
  departments: string[]
  academies: string[]
  eventAddressType: string
  categories: string[][]
  geolocRadius: number
}

export const OffersSearch = ({
  venueFilter,
  setGeoRadius,
}: SearchProps): JSX.Element => {
  const { setFacetFilters } = useContext(FacetFiltersContext)
  const { adageUser } = useAdageUser()
  const [categoriesOptions, setCategoriesOptions] = useState<
    Option<string[]>[]
  >([])

  const notification = useNotification()

  const [domainsOptions, setDomainsOptions] = useState<Option<number>[]>([])

  useEffect(() => {
    const getAllCategories = async () => {
      try {
        const result = await apiAdage.getEducationalOffersCategories()

        return setCategoriesOptions(filterEducationalSubCategories(result))
      } catch {
        notification.error(GET_DATA_ERROR_MESSAGE)
      }
    }
    const getAllDomains = async () => {
      try {
        const result = await api.listEducationalDomains()

        return setDomainsOptions(
          result.map(({ id, name }) => ({ value: id, label: name }))
        )
      } catch {
        notification.error(GET_DATA_ERROR_MESSAGE)
      }
    }
    getAllCategories()
    getAllDomains()
  }, [])

  const handleSubmit = () => {
    const updatedFilters = adageFiltersToFacetFilters({
      ...formik.values,
      uai: adageUser.uai ? ['all', adageUser.uai] : ['all'],
    })

    setFacetFilters(updatedFilters.queryFilters)

    const adageUserHasValidGeoloc =
      (adageUser.lat || adageUser.lat === 0) &&
      (adageUser.lon || adageUser.lon === 0)
    if (adageUserHasValidGeoloc) {
      setGeoRadius(
        localisationFilterState === LocalisationFilterStates.GEOLOCATION
          ? formik.values.geolocRadius * 1000
          : null
      )
    }
  }

  const resetForm = () => {
    setlocalisationFilterState(LocalisationFilterStates.NONE)
    formik.setValues(ADAGE_FILTERS_DEFAULT_VALUES)
    formik.handleSubmit()
  }
  const [currentSearch, setCurrentSearch] = useState<string | null>(null)
  const logFiltersOnSearch = (nbHits: number, queryId?: string) => {
    /* istanbul ignore next: TO FIX the current structure make it hard to test, we probably should not mock Offers in OfferSearch tests */
    if (formik.submitCount > 0 || currentSearch !== null) {
      apiAdage.logTrackingFilter({
        iframeFrom: removeParamsFromUrl(location.pathname),
        resultNumber: nbHits,
        queryId: queryId ?? null,
        filterValues: formik
          ? serializeFiltersForData(
              formik.values,
              currentSearch,
              categoriesOptions,
              domainsOptions
            )
          : {},
      })
    }
  }

  const formik = useFormik<SearchFormValues>({
    initialValues: computeFiltersInitialValues(venueFilter),
    enableReinitialize: true,
    onSubmit: handleSubmit,
  })
  const getActiveLocalisationFilter = () => {
    if (formik.values.departments.length > 0) {
      return LocalisationFilterStates.DEPARTMENTS
    }
    if (formik.values.academies.length > 0) {
      return LocalisationFilterStates.ACADEMIES
    }
    return LocalisationFilterStates.NONE
  }
  const [localisationFilterState, setlocalisationFilterState] =
    useState<LocalisationFilterStates>(getActiveLocalisationFilter())

  const offerFilterRef = useRef<HTMLDivElement>(null)
  const isOfferFiltersVisible = useIsElementVisible(offerFilterRef)
  return (
    <>
      <FormikContext.Provider value={formik}>
        <Autocomplete
          initialQuery={venueFilter?.publicName || venueFilter?.name || ''}
          placeholder={
            'Rechercher par mot-clé, par partenaire culturel, par nom d’offre...'
          }
          setCurrentSearch={setCurrentSearch}
        />
        <div ref={offerFilterRef}>
          <OfferFilters
            className={styles['search-filters']}
            localisationFilterState={localisationFilterState}
            setLocalisationFilterState={setlocalisationFilterState}
            resetForm={resetForm}
            categoriesOptions={categoriesOptions}
            domainsOptions={domainsOptions}
          />
        </div>
      </FormikContext.Provider>
      <div className="search-results">
        <Offers
          logFiltersOnSearch={logFiltersOnSearch}
          submitCount={formik.submitCount}
          isBackToTopVisibile={!isOfferFiltersVisible}
        />
      </div>
    </>
  )
}
