import classnames from 'classnames'
import { FormikProvider, useFormik } from 'formik'
import isEqual from 'lodash.isequal'
import { useState, useEffect, useRef } from 'react'
import { useSelector } from 'react-redux'
import * as yup from 'yup'

import { useVenuesFromOfferer } from 'commons/hooks/swr/useVenuesFromOfferer'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { useIncome } from 'pages/Reimbursements/Income/useIncome'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Income.module.scss'
import { IncomeError } from './IncomeError/IncomeError'
import { IncomeNoData } from './IncomeNoData/IncomeNoData'
import { IncomeResultsBox } from './IncomeResultsBox/IncomeResultsBox'

type VenueFormValues = {
  selectedVenues: string[]
  'search-selectedVenues': string
}

export const Income = () => {
  const firstYearFilterRef = useRef<HTMLButtonElement>(null)

  const [previouslySelectedOffererId, setPreviouslySelectedOffererId] =
    useState<number | null>(null)
  const [debouncedSelectedVenues, setDebouncedSelectedVenues] = useState<
    string[]
  >([])
  const [activeYear, setActiveYear] = useState<number>()

  const selectedOffererId = useSelector(selectCurrentOffererId)
  const {
    data: venues,
    isLoading: areVenuesLoading,
    error: venuesApiError,
  } = useVenuesFromOfferer(selectedOffererId)
  const hasVenuesData = venues.length > 0
  const venuesDataReady = !areVenuesLoading && !venuesApiError && hasVenuesData
  const hasSingleVenue = venuesDataReady && venues.length === 1
  const venueValues = venues.map((v: {
    value: string
    label: string
  }) => v.value)

  const formik = useFormik<VenueFormValues>({
    // SelectAutocomplete has two fields:
    // - selectedVenues: for the <select> menu & SelectedValuesTags
    // - 'search-selectedVenues': for the search input
    initialValues: {
      selectedVenues: venueValues,
      'search-selectedVenues': '',
    },
    validationSchema: yup.object().shape({
      selectedVenues: yup.array().test({
        name: 'selectedVenues',
        message: 'Vous devez sélectionner au moins un partenaire',
        test: (value) => {
          return (value || []).length > 0
        },
      }),
      'search-selectedVenues': yup.string(),
    }),
    enableReinitialize: true,
    onSubmit: () => {},
  })

  useEffect(() => {
    const newSelectedVenues = [...formik.values.selectedVenues]
    const selectionHasChanged = !isEqual(
      newSelectedVenues,
      debouncedSelectedVenues
    )

    if (selectionHasChanged) {
      if (selectedOffererId !== previouslySelectedOffererId) {
        // Offerer has changed.
        setDebouncedSelectedVenues(newSelectedVenues)
        setPreviouslySelectedOffererId(selectedOffererId)
      } else if (newSelectedVenues.length !== 0) {
        // Venues have changed.
        const debounced = setTimeout(() => {
          setDebouncedSelectedVenues(newSelectedVenues)
          setActiveYear(undefined)
        }, 1000)
        return () => clearTimeout(debounced)
      }
    }

    return
  }, [selectedOffererId, formik.values])

  const {
    isIncomeLoading,
    incomeApiError,
    incomeDataReady,
    incomeByYear,
    years,
  } = useIncome(debouncedSelectedVenues)
  const finalActiveYear = activeYear || years[0]
  const activeYearIncome = incomeByYear?.[finalActiveYear] || {}
  const activeYearHasData =
    activeYearIncome.revenue || activeYearIncome.expectedRevenue

  useEffect(() => {
    if (hasSingleVenue && incomeDataReady && firstYearFilterRef.current) {
      // If there is only one venue, the venue selector will not be displayed
      // and the first year filter will be auto-focused as soon as the data is loaded.
      firstYearFilterRef.current.focus()
    }
  }, [hasSingleVenue, incomeDataReady])

  return (
    <>
      <div role="status">
        {!venuesDataReady && (
          <>
            {areVenuesLoading ? (
              <Spinner testId="venues-spinner" />
            ) : venuesApiError ? (
              <IncomeError />
            ) : (
              <IncomeNoData type="venues" />
            )}
          </>
        )}
      </div>
      {venuesDataReady && (
        <>
          {!hasSingleVenue && <FormLayout.MandatoryInfo />}
          <div className={styles['income-filters']}>
            <FormikProvider value={formik}>
              {!hasSingleVenue && (
                <SelectAutocomplete
                  className={styles['income-filters-by-venue']}
                  selectedValuesTagsClassName={
                    styles['income-filters-by-venue-selected-tags']
                  }
                  name="selectedVenues"
                  label="Partenaire(s) sélectionné(s)"
                  options={venues}
                  multi
                  shouldFocusOnMount
                  preventOpenOnFirstFocus
                />
              )}
            </FormikProvider>
            {incomeDataReady && (
              <>
                {!hasSingleVenue && (
                  <span className={styles['income-filters-divider']} />
                )}
                <ul
                  className={classnames(styles['income-filters-by-year'], {
                    [styles['income-filters-by-year-is-only-filter']]:
                      hasSingleVenue,
                  })}
                  aria-label="Filtrage par année"
                >
                  {years.map((year) => (
                    <li key={year}>
                      <button
                        id={`income-filter-by-year-${year}-${year === finalActiveYear}`}
                        {...(year === finalActiveYear
                          ? { ref: firstYearFilterRef }
                          : {})}
                        type="button"
                        onClick={() => setActiveYear(year)}
                        aria-label={`Afficher les revenus de l'année ${year}`}
                        aria-controls="income-results"
                        aria-current={year === finalActiveYear}
                        className={classnames(
                          styles['income-filters-by-year-button'],
                          {
                            [styles['income-filters-by-year-button-active']]:
                              year === finalActiveYear,
                          }
                        )}
                      >
                        {year}
                      </button>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
          <div id="income-results" role="status">
            {!incomeDataReady && (
              <>
                {isIncomeLoading ? (
                  <Spinner testId="income-spinner" />
                ) : incomeApiError ? (
                  <IncomeError />
                ) : (
                  <IncomeNoData type="income" />
                )}
              </>
            )}
            {incomeDataReady && (
              <>
                {!activeYearHasData ? (
                  <IncomeNoData type="income-year" />
                ) : (
                  <div className={styles['income-results']}>
                    {activeYearIncome.revenue && (
                      <IncomeResultsBox
                        type="revenue"
                        income={activeYearIncome.revenue}
                      />
                    )}
                    {activeYearIncome.expectedRevenue && (
                      <IncomeResultsBox
                        type="expectedRevenue"
                        income={activeYearIncome.expectedRevenue}
                      />
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}
    </>
  )
}
