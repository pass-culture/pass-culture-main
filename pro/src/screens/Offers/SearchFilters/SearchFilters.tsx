import { endOfDay } from 'date-fns'
import React, { useCallback } from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Audience, Offerer, Option, TSearchFilters } from 'core/Offers/types'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'

import CollectiveSearchFilters from './CollectiveSearchFilters'
import IndividualSearchFilters from './IndividualSearchFilters'
import styles from './SearchFilters.module.scss'

interface ISearchFiltersProps {
  applyFilters: () => void
  offerer: Offerer | null
  removeOfferer: () => void
  selectedFilters: TSearchFilters
  setSearchFilters: (
    filters:
      | TSearchFilters
      | ((previousFilters: TSearchFilters) => TSearchFilters)
  ) => void
  disableAllFilters: boolean
  userHasSearchFilters: boolean
  resetFilters: () => void
  venues: Option[]
  categories: Option[]
  audience: Audience
}

const SearchFilters = ({
  applyFilters,
  offerer,
  removeOfferer,
  selectedFilters,
  setSearchFilters,
  disableAllFilters,
  userHasSearchFilters,
  resetFilters,
  venues,
  categories,
  audience,
}: ISearchFiltersProps): JSX.Element => {
  const updateSearchFilters = useCallback(
    (newSearchFilters: Partial<TSearchFilters>) => {
      setSearchFilters(currentSearchFilters => ({
        ...currentSearchFilters,
        ...newSearchFilters,
      }))
    },
    [setSearchFilters]
  )

  const storeNameOrIsbnSearchValue = useCallback(
    event => {
      updateSearchFilters({ nameOrIsbn: event.target.value })
    },
    [updateSearchFilters]
  )

  const storeSelectedVenue = useCallback(
    event => {
      updateSearchFilters({ venueId: event.target.value })
    },
    [updateSearchFilters]
  )

  const storeSelectedCategory = useCallback(
    event => {
      updateSearchFilters({ categoryId: event.target.value })
    },
    [updateSearchFilters]
  )

  const storeCreationMode = useCallback(
    event => {
      updateSearchFilters({ creationMode: event.target.value })
    },
    [updateSearchFilters]
  )

  const changePeriodBeginningDateValue = useCallback(
    periodBeginningDate => {
      const dateToFilter = periodBeginningDate
        ? formatBrowserTimezonedDateAsUTC(periodBeginningDate)
        : DEFAULT_SEARCH_FILTERS.periodBeginningDate
      updateSearchFilters({ periodBeginningDate: dateToFilter })
    },
    [updateSearchFilters]
  )

  const changePeriodEndingDateValue = useCallback(
    periodEndingDate => {
      const dateToFilter = periodEndingDate
        ? formatBrowserTimezonedDateAsUTC(endOfDay(periodEndingDate))
        : DEFAULT_SEARCH_FILTERS.periodEndingDate
      updateSearchFilters({ periodEndingDate: dateToFilter })
    },
    [updateSearchFilters]
  )

  const requestFilteredOffers = useCallback(
    event => {
      event.preventDefault()
      applyFilters()
    },
    [applyFilters]
  )

  return (
    <>
      {offerer && (
        <span className="offerer-filter">
          {offerer.name}
          <button onClick={removeOfferer} type="button">
            <Icon alt="Supprimer le filtre par structure" svg="ico-close-b" />
          </button>
        </span>
      )}
      <form onSubmit={requestFilteredOffers}>
        {audience === Audience.INDIVIDUAL ? (
          <IndividualSearchFilters
            categoriesOptions={categories}
            changePeriodBeginningDateValue={changePeriodBeginningDateValue}
            changePeriodEndingDateValue={changePeriodEndingDateValue}
            disableAllFilters={disableAllFilters}
            selectedFilters={selectedFilters}
            storeCreationMode={storeCreationMode}
            storeNameOrIsbnSearchValue={storeNameOrIsbnSearchValue}
            storeSelectedCategory={storeSelectedCategory}
            storeSelectedVenue={storeSelectedVenue}
            venueOptions={venues}
          />
        ) : (
          <CollectiveSearchFilters
            categoriesOptions={categories}
            changePeriodBeginningDateValue={changePeriodBeginningDateValue}
            changePeriodEndingDateValue={changePeriodEndingDateValue}
            disableAllFilters={disableAllFilters}
            selectedFilters={selectedFilters}
            storeNameOrIsbnSearchValue={storeNameOrIsbnSearchValue}
            storeSelectedCategory={storeSelectedCategory}
            storeSelectedVenue={storeSelectedVenue}
            venueOptions={venues}
          />
        )}
        {userHasSearchFilters ? (
          <Link
            className="reset-filters-link"
            onClick={resetFilters}
            to={`/offres${
              audience === Audience.COLLECTIVE ? '?audience=collective' : ''
            }`}
          >
            <ResetIcon className="reset-filters-link-icon" />
            Réinitialiser les filtres
          </Link>
        ) : (
          <span className="reset-filters-link disabled">
            <ResetIcon className="reset-filters-link-icon" />
            Réinitialiser les filtres
          </span>
        )}
        <div className={styles['search-separator']}>
          <div className={styles['separator']} />
          <button
            className="primary-button"
            disabled={disableAllFilters}
            type="submit"
          >
            Lancer la recherche
          </button>
          <div className={styles['separator']} />
        </div>
      </form>
    </>
  )
}

export default SearchFilters
