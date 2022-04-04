import cn from 'classnames'
import { endOfDay } from 'date-fns'
import { utcToZonedTime } from 'date-fns-tz'
import React, { useCallback } from 'react'
import { Link } from 'react-router-dom'

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
import { Audience, Offerer, Option, TSearchFilters } from 'core/Offers/types'
import { hasSearchFilters } from 'core/Offers/utils'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import { formatBrowserTimezonedDateAsUTC, getToday } from 'utils/date'

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

  const searchByOfferNameLabel =
    audience === Audience.INDIVIDUAL
      ? 'Nom de l’offre ou ISBN'
      : 'Nom de l’offre'
  const searchByOfferNamePlaceholder =
    audience === Audience.INDIVIDUAL
      ? 'Rechercher par nom d’offre ou par ISBN'
      : 'Rechercher par nom d’offre'

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
          disabled={disableAllFilters}
          label={searchByOfferNameLabel}
          name="offre"
          onChange={storeNameOrIsbnSearchValue}
          placeholder={searchByOfferNamePlaceholder}
          value={selectedFilters.nameOrIsbn}
        />
        <div
          className={
            audience === Audience.INDIVIDUAL
              ? 'form-row'
              : 'collective-form-row'
          }
        >
          <Select
            defaultOption={ALL_VENUES_OPTION}
            handleSelection={storeSelectedVenue}
            isDisabled={disableAllFilters}
            label="Lieu"
            name="lieu"
            options={venues}
            selectedValue={selectedFilters.venueId}
          />
          <Select
            defaultOption={ALL_CATEGORIES_OPTION}
            handleSelection={storeSelectedCategory}
            isDisabled={disableAllFilters}
            label="Catégories"
            name="categorie"
            options={categories}
            selectedValue={selectedFilters.categoryId}
          />
          {audience === Audience.INDIVIDUAL && (
            <Select
              defaultOption={DEFAULT_CREATION_MODE}
              handleSelection={storeCreationMode}
              isDisabled={disableAllFilters}
              label="Mode de création"
              name="creationMode"
              options={CREATION_MODES_FILTERS}
              selectedValue={selectedFilters.creationMode}
            />
          )}
          <PeriodSelector
            changePeriodBeginningDateValue={changePeriodBeginningDateValue}
            changePeriodEndingDateValue={changePeriodEndingDateValue}
            isDisabled={disableAllFilters}
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
        {hasSearchFilters(selectedFilters) ? (
          <Link
            className={styles['reset-filters-link']}
            onClick={resetFilters}
            to={`/offres${
              audience === Audience.COLLECTIVE ? '/collectives' : ''
            }`}
          >
            <ResetIcon className={styles['reset-filters-link-icon']} />
            Réinitialiser les filtres
          </Link>
        ) : (
          <span
            className={cn(styles['reset-filters-link'], styles['disabled'])}
          >
            <ResetIcon className={styles['reset-filters-link-icon']} />
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
