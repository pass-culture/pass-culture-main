import classnames from 'classnames'
import { useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_VENUES_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { noop } from '@/commons/utils/noop'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { useIncome } from '@/pages/Reimbursements/Income/useIncome'
import { formatAndOrderVenues } from '@/repository/venuesService'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from './Income.module.scss'
import { IncomeError } from './IncomeError/IncomeError'
import { IncomeNoData } from './IncomeNoData/IncomeNoData'
import { IncomeResultsBox } from './IncomeResultsBox/IncomeResultsBox'

type Option = {
  id: string
  label: string
}

type VenueFormValues = {
  selectedVenues: Option[]
}

export const Income = () => {
  const firstYearFilterRef = useRef<HTMLButtonElement>(null)
  const [activeYear, setActiveYear] = useState<number>()
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const adminSelectedOfferer = useAppSelector(
    (store) => store.offerer.adminCurrentOfferer
  )

  const offererId = withSwitchVenueFeature
    ? adminSelectedOfferer?.id
    : selectedOffererId

  const {
    data: venuesData,
    isLoading: areVenuesLoading,
    error: venuesApiError,
  } = useSWR([GET_VENUES_QUERY_KEY, offererId], () =>
    api.getVenues(true, null, offererId)
  )

  const venueValues = formatAndOrderVenues(venuesData?.venues ?? []).map(
    (venue) => ({
      id: String(venue.value),
      label: venue.label,
    })
  )

  const {
    register,
    watch,
    setValue,
    setError,
    clearErrors,
    formState: { errors },
  } = useForm<VenueFormValues>({
    values: {
      selectedVenues: venueValues,
    },
  })

  const selectedWatch = watch('selectedVenues')
  const selected = selectedWatch.map((v) => v.id)

  const hasVenuesData = venueValues.length > 0
  const hasSingleVenue = venueValues.length === 1

  const onChange = (selectedOption: Option[]) => {
    if (selectedOption.length === 0) {
      setError('selectedVenues', {
        message: 'Vous devez sélectionner au moins un partenaire',
      })
    } else {
      clearErrors('selectedVenues')
    }

    const debounced = setTimeout(() => {
      setValue(
        'selectedVenues',
        selectedOption.map((v) => v)
      )
    }, 1000)
    return () => clearTimeout(debounced)
  }

  const {
    isIncomeLoading,
    incomeApiError,
    incomeDataReady,
    incomeByYear,
    hasIncomeData,
    years,
  } = useIncome(selected)

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

  if (areVenuesLoading) {
    return <Spinner testId="venues-spinner" />
  }

  if (venuesApiError) {
    return <IncomeError />
  }

  return (
    <>
      {!hasVenuesData ? (
        <IncomeNoData type="venues" />
      ) : (
        <>
          {!hasSingleVenue && (
            <>
              <FormLayout.MandatoryInfo />
              <div className={styles['income-filters']}>
                <MultiSelect
                  {...register('selectedVenues', { minLength: 1 })}
                  required={true}
                  buttonLabel="Partenaire(s) sélectionné(s)"
                  className={styles['income-input']}
                  label="Partenaire(s) sélectionné(s)"
                  options={venueValues}
                  defaultOptions={venueValues}
                  hasSearch
                  searchLabel="Rechercher un partenaire"
                  onSelectedOptionsChanged={(selectedOption) =>
                    onChange(selectedOption)
                  }
                  error={errors.selectedVenues?.message}
                  onBlur={() => noop}
                />
              </div>
            </>
          )}

          {isIncomeLoading ? (
            <Spinner testId="income-spinner" />
          ) : incomeApiError ? (
            <div role="alert">
              <IncomeError />
            </div>
          ) : !hasIncomeData ? (
            <IncomeNoData type="income" />
          ) : (
            <>
              <ul
                className={classnames(
                  styles['income-filters'],
                  styles['income-filters-by-year'],
                  {
                    [styles['income-filters-by-year-is-only-filter']]:
                      hasSingleVenue,
                  }
                )}
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

              {!activeYearHasData ? (
                <IncomeNoData type="income-year" />
              ) : (
                <div className={styles['income-results']}>
                  {activeYearIncome.revenue && (
                    <div className={styles['income-box']}>
                      <IncomeResultsBox
                        type="revenue"
                        income={activeYearIncome.revenue}
                      />
                    </div>
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
        </>
      )}
    </>
  )
}
