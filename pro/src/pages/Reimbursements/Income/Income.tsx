import isEqual from 'lodash.isequal'
import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import { useAnalytics } from 'app/App/analytics/firebase'
import { GET_VENUES_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeBookingHoldIcon from 'icons/stroke-booking-hold.svg'
import strokePageNotFoundIcon from 'icons/stroke-page-not-found.svg'
import { formatAndOrderVenues } from 'repository/venuesService'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Income.module.scss'
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
  const { logEvent } = useAnalytics()
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

  const [isIncomeLoading, setIsIncomeLoading] = useState(false)
  const [incomeApiError] = useState<Error>()

  const [selectedVenues, setSelectedVenues] = useState<string[]>([])
  const [incomeByYear, setIncomeByYear] = useState<IncomeByYear>()
  const [activeYear, setActiveYear] = useState<number>()

  const years = Object.keys(incomeByYear || {})
    .map(Number)
    .sort((a, b) => b - a)
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

  if (areVenuesLoading || isIncomeLoading) {
    return <Spinner />
  }

  if (venuesApiError || incomeApiError) {
    return (
      <div className={styles['income-error']}>
        <SvgIcon
          className={styles['icon']}
          src={strokePageNotFoundIcon}
          viewBox="0 0 130 100"
          alt=""
          width="100"
        />
        Erreur dans le chargement des données.
      </div>
    )
  }

  return (
    <>
      <FormLayout.MandatoryInfo />
      <div className={styles['income-filters']}>
        {venues.length > 1 && (
          <>
            <IncomeVenueSelector
              venues={venues}
              onChange={(venues) => {
                if (!isEqual(selectedVenues, venues)) {
                  setSelectedVenues(venues)
                }
              }}
            />
            <span className={styles['income-filters-divider']} />
          </>
        )}
        <ul
          className={styles['income-year-filters']}
          aria-label="Filtrage par année"
        >
          {years.map((year) => (
            <li
              key={year}
              className={year === activeYear ? styles['active-year'] : ''}
            >
              <button
                type="button"
                onClick={() => setActiveYear(year)}
                aria-label={`Afficher les revenus de l'année ${year}`}
                aria-controls="income-results"
                aria-current={year === activeYear}
              >
                {year}
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div id="income-results" role="status">
        {activeYearHasData ? (
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
        ) : (
          <div className={styles['income-no-data']}>
            <SvgIcon
              className={styles['icon']}
              src={strokeBookingHoldIcon}
              alt=""
              width="128"
            />
            Vous n’avez aucune réservation sur cette période.
            <div className={styles['text-with-link']}>
              Découvrez nos
              <ButtonLink
                isExternal
                opensInNewTab
                to="https://passcultureapp.notion.site/pass-Culture-Documentation-323b1a0ec309406192d772e7d803fbd0"
                className={styles['link']}
                onClick={() =>
                  logEvent(Events.CLICKED_BEST_PRACTICES_STUDIES, {
                    from: location.pathname,
                  })
                }
              >
                Bonnes pratiques & Études
              </ButtonLink>
              pour optimiser la visibilité de vos offres.
            </div>
          </div>
        )}
      </div>
    </>
  )
}
