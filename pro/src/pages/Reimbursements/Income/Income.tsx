import classnames from 'classnames'
import { useEffect, useRef, useState } from 'react'
import { useForm } from 'react-hook-form'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedAdminOfferer } from '@/commons/store/user/selectors'
import { noop } from '@/commons/utils/noop'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { useIncome } from '@/pages/Reimbursements/Income/useIncome'
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

const Income = () => {
  const firstYearFilterRef = useRef<HTMLButtonElement>(null)
  const [activeYear, setActiveYear] = useState<number>()

  const venues = useAppSelector((state) => state.user.venues)
  const selectedAdminOfferer = useAppSelector(ensureSelectedAdminOfferer)

  const venueValues = (venues ?? [])
    .filter((venue) => venue.managingOffererId === selectedAdminOfferer?.id)
    .map((venue) => ({
      id: String(venue.id),
      label: venue.publicName,
    }))
    .sort((a, b) =>
      a.label.localeCompare(b.label, 'fr', { sensitivity: 'base' })
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
                  styles['income-filters-by-year']
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
                <div>
                  {activeYearIncome.revenue && (
                    <div className={styles['income-box']}>
                      <IncomeResultsBox
                        type="revenue"
                        income={activeYearIncome.revenue}
                        isCaledonian={selectedAdminOfferer?.isCaledonian}
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

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Income
