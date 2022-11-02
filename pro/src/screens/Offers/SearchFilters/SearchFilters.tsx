import { endOfDay } from 'date-fns'
import { utcToZonedTime } from 'date-fns-tz'
import React, { FormEvent, MouseEventHandler, useCallback } from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import {
  ALL_CATEGORIES_OPTION,
  ALL_VENUES_OPTION,
  COLLECTIVE_OFFER_TYPES_FILTERS,
  CREATION_MODES_FILTERS,
  DEFAULT_COLLECTIVE_OFFER_TYPE,
  DEFAULT_CREATION_MODE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offerer, Option, TSearchFilters } from 'core/Offers/types'
import { hasSearchFilters } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'
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
  resetFilters: MouseEventHandler<HTMLAnchorElement>
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
    (event: FormEvent<HTMLSelectElement>) => {
      updateSearchFilters({ nameOrIsbn: event.currentTarget.value })
    },
    [updateSearchFilters]
  )

  const storeSelectedVenue = useCallback(
    (event: FormEvent<HTMLSelectElement>) => {
      updateSearchFilters({ venueId: event.currentTarget.value })
    },
    [updateSearchFilters]
  )

  const storeSelectedCategory = useCallback(
    (event: FormEvent<HTMLSelectElement>) => {
      updateSearchFilters({ categoryId: event.currentTarget.value })
    },
    [updateSearchFilters]
  )

  const storeCreationMode = useCallback(
    (event: FormEvent<HTMLSelectElement>) => {
      updateSearchFilters({ creationMode: event.currentTarget.value })
    },
    [updateSearchFilters]
  )

  const storeCollectiveOfferType = useCallback(
    (event: FormEvent<HTMLSelectElement>) => {
      updateSearchFilters({ collectiveOfferType: event.currentTarget.value })
    },
    [updateSearchFilters]
  )

  const changePeriodBeginningDateValue = useCallback(
    (periodBeginningDate: Date) => {
      const dateToFilter = periodBeginningDate
        ? formatBrowserTimezonedDateAsUTC(periodBeginningDate)
        : DEFAULT_SEARCH_FILTERS.periodBeginningDate
      updateSearchFilters({ periodBeginningDate: dateToFilter })
    },
    [updateSearchFilters]
  )

  const changePeriodEndingDateValue = useCallback(
    (periodEndingDate: Date) => {
      const dateToFilter = periodEndingDate
        ? formatBrowserTimezonedDateAsUTC(endOfDay(periodEndingDate))
        : DEFAULT_SEARCH_FILTERS.periodEndingDate
      updateSearchFilters({ periodEndingDate: dateToFilter })
    },
    [updateSearchFilters]
  )

  const requestFilteredOffers = useCallback(
    (event: FormEvent) => {
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
  const resetFilterButtonProps = !hasSearchFilters(selectedFilters)
    ? { 'aria-current': 'page', isDisabled: true }
    : {}

  const isCollectiveOfferDuplicationActive = useActiveFeature(
    'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE'
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
          disabled={disableAllFilters}
          label={searchByOfferNameLabel}
          name="offre"
          onChange={storeNameOrIsbnSearchValue}
          placeholder={searchByOfferNamePlaceholder}
          value={selectedFilters.nameOrIsbn}
        />
        <div
          className={
            audience === Audience.INDIVIDUAL ||
            isCollectiveOfferDuplicationActive
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
          {audience === Audience.COLLECTIVE &&
            isCollectiveOfferDuplicationActive && (
              <Select
                defaultOption={DEFAULT_COLLECTIVE_OFFER_TYPE}
                handleSelection={storeCollectiveOfferType}
                isDisabled={disableAllFilters}
                label="Type de l'offre"
                name="collectiveOfferType"
                options={COLLECTIVE_OFFER_TYPES_FILTERS}
                selectedValue={selectedFilters.collectiveOfferType}
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
        <div className={styles['reset-filters']}>
          <ButtonLink
            Icon={ResetIcon}
            {...resetFilterButtonProps}
            onClick={resetFilters}
            link={{
              to: `/offres${
                audience === Audience.COLLECTIVE ? '/collectives' : ''
              }`,
              isExternal: false,
            }}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </ButtonLink>
        </div>
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
