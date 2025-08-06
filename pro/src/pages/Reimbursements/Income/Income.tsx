import classnames from 'classnames'
import { useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'

import { useVenuesFromOfferer } from '@/commons/hooks/swr/useVenuesFromOfferer'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { useIncome } from '@/pages/Reimbursements/Income/useIncome'
import { MultiSelect } from '@/ui-kit/MultiSelect/MultiSelect'
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
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const {
    data: venues,
    isLoading: areVenuesLoading,
    error: venuesApiError,
  } = useVenuesFromOfferer(selectedOffererId)

  const venueValues = venues.map((v) => ({
    id: v.value,
    label: v.label,
  }))

  const {
    register,
    watch,
    setValue,
    setError,
    reset,
    formState: { errors },
  } = useForm<VenueFormValues>({
    values: {
      selectedVenues: venueValues,
    },
  })

  const selectedWatch = watch('selectedVenues')
  const selected = selectedWatch.map((v) => v.id)

  const hasVenuesData = venues.length > 0
  const hasSingleVenue = venues.length === 1

  const onChange = (selectedOption: any[]) => {
    if (selectedOption.length === 0) {
      setError('selectedVenues', {
        message: 'Vous devez sélectionner au moins un partenaire',
      })
    } else {
      reset()
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
                  searchLabel="Recherche"
                  onSelectedOptionsChanged={(selectedOption) =>
                    onChange(selectedOption)
                  }
                  error={errors.selectedVenues?.message}
                  onBlur={() => {}}
                />
              </div>
            </>
          )}

          {isIncomeLoading ? (
            <div id="income-results" role="status">
              <Spinner testId="income-spinner" />
            </div>
          ) : incomeApiError ? (
            <div id="income-results" role="status">
              <IncomeError />
            </div>
          ) : (
            <>
              {!hasIncomeData ? (
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
      )}
    </>
  )
}
