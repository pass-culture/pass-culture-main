import { endOfDay } from 'date-fns'
import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { api } from 'api/v1/api'
import Icon from 'components/layout/Icon'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { Offerer, TSearchFilters } from 'core/Offers/types'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import {
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from 'repository/venuesService'
import { formatBrowserTimezonedDateAsUTC } from 'utils/date'

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
}: ISearchFiltersProps): JSX.Element => {
  const [categoriesOptions, setCategoriesOptions] = useState<
    { id: string; displayName: string }[]
  >([])
  const [venueOptions, setVenueOptions] = useState([])

  useEffect(() => {
    api.getOffersGetCategories().then(categoriesAndSubcategories => {
      const { categories } = categoriesAndSubcategories
      const categoriesOptions = categories
        .filter(category => category.isSelectable)
        .map(category => ({
          id: category.id,
          displayName: category.proLabel,
        }))
      setCategoriesOptions(
        categoriesOptions.sort((a, b) =>
          a.displayName.localeCompare(b.displayName)
        )
      )
    })
    fetchAllVenuesByProUser(offerer?.id).then(venues =>
      setVenueOptions(formatAndOrderVenues(venues))
    )
  }, [offerer?.id])

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
        <IndividualSearchFilters
          categoriesOptions={categoriesOptions}
          changePeriodBeginningDateValue={changePeriodBeginningDateValue}
          changePeriodEndingDateValue={changePeriodEndingDateValue}
          disableAllFilters={disableAllFilters}
          selectedFilters={selectedFilters}
          storeCreationMode={storeCreationMode}
          storeNameOrIsbnSearchValue={storeNameOrIsbnSearchValue}
          storeSelectedCategory={storeSelectedCategory}
          storeSelectedVenue={storeSelectedVenue}
          venueOptions={venueOptions}
        />
        {userHasSearchFilters ? (
          <Link
            className="reset-filters-link"
            onClick={resetFilters}
            to="/offres"
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
