import classnames from 'classnames'
import { useEffect, useRef, useState } from 'react'

import type { GetOffererResponseModel } from '@/apiClient/v1'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import styles from '../Income.module.scss'
import { IncomeError } from '../IncomeError/IncomeError'
import { IncomeNoData } from '../IncomeNoData/IncomeNoData'
import { IncomeResultsBox } from '../IncomeResultsBox/IncomeResultsBox'
import { useIncome } from '../useIncome'

interface IncomeDataProps {
  selected: string[]
  hasSingleVenue: boolean
  selectedAdminOfferer: GetOffererResponseModel
}

export const IncomeData = ({
  selected,
  hasSingleVenue,
  selectedAdminOfferer,
}: IncomeDataProps) => {
  const firstYearFilterRef = useRef<HTMLButtonElement>(null)
  const [activeYear, setActiveYear] = useState<number>()
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
  const hasNoVenuesSelected = selected.length === 0

  useEffect(() => {
    if (hasSingleVenue && incomeDataReady && firstYearFilterRef.current) {
      // If there is only one venue, the venue selector will not be displayed
      // and the first year filter will be auto-focused as soon as the data is loaded.
      firstYearFilterRef.current.focus()
    }
  }, [hasSingleVenue, incomeDataReady])

  if (isIncomeLoading) {
    return <Spinner testId="income-spinner" />
  } else if (incomeApiError) {
    return (
      <div role="alert">
        <IncomeError />
      </div>
    )
  } else if (hasNoVenuesSelected) {
    return <IncomeNoData type="no-venues-selected" />
  } else if (!hasIncomeData) {
    return <IncomeNoData type="income" />
  } else {
    return (
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
                ref={year === finalActiveYear ? firstYearFilterRef : undefined}
                type="button"
                onClick={() => setActiveYear(year)}
                aria-label={`Afficher les revenus de l'année ${year}`}
                aria-current={year === finalActiveYear}
                className={classnames(styles['income-filters-by-year-button'], {
                  [styles['income-filters-by-year-button-active']]:
                    year === finalActiveYear,
                })}
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
    )
  }
}
