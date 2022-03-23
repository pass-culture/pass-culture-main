import { endOfDay } from 'date-fns'
import { utcToZonedTime } from 'date-fns-tz'
import React, { useCallback, useEffect, useState } from 'react'

import Icon from 'components/layout/Icon'
import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import {
  ALL_CATEGORIES_OPTION,
  ALL_VENUES_OPTION,
  CREATION_MODES_FILTERS,
  DEFAULT_CREATION_MODE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offerer, SearchFilters as SearchFiltersType } from 'core/Offers/types'
import * as pcapi from 'repository/pcapi/pcapi'
import {
  fetchAllVenuesByProUser,
  formatAndOrderVenues,
} from 'repository/venuesService'
import { formatBrowserTimezonedDateAsUTC, getToday } from 'utils/date'

import styles from './SearchFilters.module.scss'

interface ISearchFiltersProps {
  applyFilters: () => void
  offerer: Offerer
  removeOfferer: () => void
  selectedFilters: SearchFiltersType
  setSearchFilters: (filters: SearchFiltersType) => void
}

const SearchFilters = ({
  applyFilters,
  offerer,
  removeOfferer,
  selectedFilters,
  setSearchFilters,
}: ISearchFiltersProps): JSX.Element => {
  const [categoriesOptions, setCategoriesOptions] = useState([])
  const [venueOptions, setVenueOptions] = useState([])

  useEffect(() => {
    pcapi.loadCategories().then(categoriesAndSubcategories => {
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
    (newSearchFilters: Partial<SearchFiltersType>) => {
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
        <TextInput
          label="Nom de l’offre ou ISBN"
          name="offre"
          onChange={storeNameOrIsbnSearchValue}
          placeholder="Rechercher par nom d’offre ou par ISBN"
          value={selectedFilters.nameOrIsbn}
        />
        <div className="form-row">
          <Select
            defaultOption={ALL_VENUES_OPTION}
            handleSelection={storeSelectedVenue}
            label="Lieu"
            name="lieu"
            options={venueOptions}
            selectedValue={selectedFilters.venueId}
          />
          <Select
            defaultOption={ALL_CATEGORIES_OPTION}
            handleSelection={storeSelectedCategory}
            label="Catégories"
            name="categorie"
            options={categoriesOptions}
            selectedValue={selectedFilters.categoryId}
          />
          <Select
            defaultOption={DEFAULT_CREATION_MODE}
            handleSelection={storeCreationMode}
            label="Mode de création"
            name="creationMode"
            options={CREATION_MODES_FILTERS}
            selectedValue={selectedFilters.creationMode}
          />
          <PeriodSelector
            changePeriodBeginningDateValue={changePeriodBeginningDateValue}
            changePeriodEndingDateValue={changePeriodEndingDateValue}
            isDisabled={false}
            label="Période de l’évènement"
            periodBeginningDate={
              selectedFilters.periodBeginningDate
                ? utcToZonedTime(selectedFilters.periodBeginningDate, 'UTC')
                : undefined
            }
            periodEndingDate={
              selectedFilters.periodEndingDate
                ? utcToZonedTime(selectedFilters.periodEndingDate, 'UTC')
                : undefined
            }
            todayDate={getToday()}
          />
        </div>
        <div className={styles['search-separator']}>
          <div className={styles['separator']} />
          <button className="primary-button" type="submit">
            Lancer la recherche
          </button>
          <div className={styles['separator']} />
        </div>
      </form>
    </>
  )
}

export default SearchFilters
