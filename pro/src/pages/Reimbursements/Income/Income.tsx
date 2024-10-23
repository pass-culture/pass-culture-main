import classnames from 'classnames'
import isEqual from 'lodash.isequal'
import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { GET_VENUES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { formatAndOrderVenues } from 'repository/venuesService'
import { Spinner } from 'ui-kit/Spinner/Spinner'

import styles from './Income.module.scss'
import { IncomeError } from './IncomeError/IncomeError'
import { IncomeNoData } from './IncomeNoData/IncomeNoData'
import { IncomeResultsBox } from './IncomeResultsBox/IncomeResultsBox'
import { IncomeVenueSelector } from './IncomeVenueSelector/IncomeVenueSelector'
import { IncomeByYear } from './types'

// FIXME: remove this, use real data.
// Follow-up Jira ticket : https://passculture.atlassian.net/browse/PC-32278
export const MOCK_INCOME_BY_YEAR: IncomeByYear = {
  2021: {},
  2022: {
    aggregatedRevenue: {
      total: 2000.27,
      individual: 2000,
    },
  },
  2023: {
    aggregatedRevenue: {
      total: 3000,
      individual: 1500,
      group: 1500,
    },
  },
  2024: {
    aggregatedRevenue: {
      total: 4000,
      individual: 2000,
      group: 2000,
    },
    expectedRevenue: {
      total: 5000,
      individual: 2500,
      group: 2500,
    },
  },
}

export const Income = () => {
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const {
    data,
    error: venuesApiError,
    isLoading: areVenuesLoading,
  } = useSWR(
    [GET_VENUES_QUERY_KEY, selectedOffererId],
    ([, offererIdParam]) => api.getVenues(null, null, offererIdParam),
    { fallbackData: { venues: [] } }
  )
  const venues = formatAndOrderVenues(data.venues)
  const venueValues = venues.map((v) => v.value)

  const [isIncomeLoading, setIsIncomeLoading] = useState(true)
  const [incomeApiError] = useState<Error>()

  const [selectedVenues, setSelectedVenues] = useState<string[]>([])
  const [incomeByYear, setIncomeByYear] = useState<IncomeByYear>()
  const [activeYear, setActiveYear] = useState<number>()

  const activeYearIncome =
    incomeByYear && activeYear ? incomeByYear[activeYear] : {}
  const activeYearHasData =
    activeYearIncome.aggregatedRevenue || activeYearIncome.expectedRevenue

  useEffect(() => {
    if (venueValues.length > 0 && selectedVenues.length === 0) {
      setSelectedVenues(venueValues)
    }
  }, [venueValues, selectedVenues])

  useEffect(() => {
    if (selectedVenues.length > 0) {
      setIsIncomeLoading(true)
      const incomeByYear = MOCK_INCOME_BY_YEAR
      setIncomeByYear(incomeByYear)

      if (!activeYear) {
        const years = Object.keys(incomeByYear)
          .map(Number)
          .sort((a, b) => a - b)
        setActiveYear(years[years.length - 1])
      }

      setIsIncomeLoading(false)
    }
  }, [selectedVenues, activeYear])

  if (areVenuesLoading) {
    return <Spinner />
  }

  if (venuesApiError) {
    return <IncomeError />
  }

  const hasVenuesData = venues.length > 0
  const hasIncomeData = incomeByYear && Object.keys(incomeByYear).length > 0

  if (!hasVenuesData) {
    return <IncomeNoData type="venues" />
  }

  return (
    <>
      <FormLayout.MandatoryInfo />
      <div className={styles['income-filters']}>
        <IncomeVenueSelector
          venues={venues}
          onChange={(venues) => {
            if (!isEqual(selectedVenues, venues)) {
              setSelectedVenues(venues)
            }
          }}
        />
        {!isIncomeLoading && !incomeApiError && hasIncomeData && (
          <>
            <span className={styles['income-filters-divider']} />
            <ul
              className={styles['income-filters-by-year']}
              aria-label="Filtrage par année"
            >
              {Object.keys(incomeByYear)
                .map(Number)
                .sort((a, b) => b - a)
                .map((year) => (
                  <li key={year}>
                    <button
                      type="button"
                      onClick={() => setActiveYear(year)}
                      aria-label={`Afficher les revenus de l'année ${year}`}
                      aria-controls="income-results"
                      aria-current={year === activeYear}
                      className={classnames(
                        styles['income-filters-by-year-button'],
                        {
                          [styles['income-filters-by-year-button-active']]:
                            year === activeYear,
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
        {isIncomeLoading ? (
          <Spinner />
        ) : incomeApiError ? (
          <IncomeError />
        ) : !hasIncomeData ? (
          <IncomeNoData type="income" />
        ) : !activeYearHasData ? (
          <IncomeNoData type="income-year" />
        ) : (
          <div className={styles['income-results']}>
            <IncomeResultsBox
              type="aggregatedRevenue"
              income={activeYearIncome.aggregatedRevenue}
            />
            <IncomeResultsBox
              type="expectedRevenue"
              income={activeYearIncome.expectedRevenue}
            />
          </div>
        )}
      </div>
    </>
  )
}
