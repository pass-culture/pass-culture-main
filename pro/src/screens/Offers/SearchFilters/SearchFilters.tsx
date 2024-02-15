import React, { FormEvent } from 'react'

import { EacFormat } from 'apiClient/v1'
import FormLayout from 'components/FormLayout/FormLayout'
import {
  ALL_CATEGORIES_OPTION,
  ALL_FORMATS_OPTION,
  ALL_VENUES_OPTION,
  COLLECTIVE_OFFER_TYPES_OPTIONS,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { Offerer, SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters } from 'core/Offers/utils'
import { Audience } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button, SubmitButton } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import PeriodSelector from 'ui-kit/form/PeriodSelector/PeriodSelector'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { BaseInput, FieldLayout } from 'ui-kit/form/shared'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './SearchFilters.module.scss'

interface SearchFiltersProps {
  applyFilters: () => void
  offerer: Offerer | null
  removeOfferer: () => void
  selectedFilters: SearchFiltersParams
  setSearchFilters: (
    filters:
      | SearchFiltersParams
      | ((previousFilters: SearchFiltersParams) => SearchFiltersParams)
  ) => void
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
  categories: SelectOption[]
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
}: SearchFiltersProps): JSX.Element => {
  const isFormatActive = useActiveFeature('WIP_ENABLE_FORMAT')

  const formats: SelectOption[] = Object.values(EacFormat).map((format) => ({
    value: format,
    label: format,
  }))

  const updateSearchFilters = (
    newSearchFilters: Partial<SearchFiltersParams>
  ) => {
    setSearchFilters((currentSearchFilters) => ({
      ...currentSearchFilters,
      ...newSearchFilters,
    }))
  }

  const storeNameOrIsbnSearchValue = (event: FormEvent<HTMLInputElement>) => {
    updateSearchFilters({ nameOrIsbn: event.currentTarget.value })
  }

  const storeSelectedVenue = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ venueId: event.currentTarget.value })
  }

  const storeSelectedCategory = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ categoryId: event.currentTarget.value })
  }

  const storeSelectedFormat = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({
      format: event.currentTarget.value as EacFormat | 'all',
    })
  }

  const storeCreationMode = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ creationMode: event.currentTarget.value })
  }

  const storeCollectiveOfferType = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ collectiveOfferType: event.currentTarget.value })
  }

  const onBeginningDateChange = (periodBeginningDate: string) => {
    const dateToFilter =
      periodBeginningDate !== ''
        ? periodBeginningDate
        : DEFAULT_SEARCH_FILTERS.periodBeginningDate
    updateSearchFilters({ periodBeginningDate: dateToFilter })
  }

  const onEndingDateChange = (periodEndingDate: string) => {
    const dateToFilter =
      periodEndingDate !== ''
        ? periodEndingDate
        : DEFAULT_SEARCH_FILTERS.periodEndingDate
    updateSearchFilters({ periodEndingDate: dateToFilter })
  }

  const requestFilteredOffers = (event: FormEvent) => {
    event.preventDefault()
    applyFilters()
  }

  const searchByOfferNameLabel =
    audience === Audience.INDIVIDUAL ? (
      <span>
        Nom de l’offre ou <abbr title="European Article Numbering">EAN-13</abbr>
      </span>
    ) : (
      'Nom de l’offre'
    )
  const searchByOfferNamePlaceholder =
    audience === Audience.INDIVIDUAL
      ? 'Rechercher par nom d’offre ou par EAN-13'
      : 'Rechercher par nom d’offre'

  return (
    <>
      {offerer && (
        <span className="offerer-filter">
          {offerer.name}
          <button
            onClick={removeOfferer}
            type="button"
            data-testid="remove-offerer-filter"
          >
            <SvgIcon
              src={strokeCloseIcon}
              alt="Supprimer le filtre par structure"
              className={styles['offerer-close-icon']}
            />
          </button>
        </span>
      )}

      <form onSubmit={requestFilteredOffers}>
        <FieldLayout label={searchByOfferNameLabel} name="offre" isOptional>
          <BaseInput
            type="text"
            disabled={disableAllFilters}
            name="offre"
            onChange={storeNameOrIsbnSearchValue}
            placeholder={searchByOfferNamePlaceholder}
            value={selectedFilters.nameOrIsbn}
          />
        </FieldLayout>

        <FormLayout.Row inline>
          <FieldLayout label="Lieu" name="lieu" isOptional>
            <SelectInput
              defaultOption={ALL_VENUES_OPTION}
              onChange={storeSelectedVenue}
              disabled={disableAllFilters}
              name="lieu"
              options={venues}
              value={selectedFilters.venueId}
            />
          </FieldLayout>

          {isFormatActive && audience === Audience.COLLECTIVE ? (
            <FieldLayout label="Format" name="format" isOptional>
              <SelectInput
                defaultOption={ALL_FORMATS_OPTION}
                onChange={storeSelectedFormat}
                disabled={disableAllFilters}
                name="format"
                options={formats}
                value={selectedFilters.format}
              />
            </FieldLayout>
          ) : (
            <FieldLayout label="Catégories" name="categorie" isOptional>
              <SelectInput
                defaultOption={ALL_CATEGORIES_OPTION}
                onChange={storeSelectedCategory}
                disabled={disableAllFilters}
                name="categorie"
                options={categories}
                value={selectedFilters.categoryId}
              />
            </FieldLayout>
          )}

          {audience === Audience.INDIVIDUAL && (
            <FieldLayout
              label="Mode de création"
              name="creationMode"
              isOptional
            >
              <SelectInput
                onChange={storeCreationMode}
                disabled={disableAllFilters}
                name="creationMode"
                options={CREATION_MODES_OPTIONS}
                value={selectedFilters.creationMode}
              />
            </FieldLayout>
          )}

          {audience === Audience.COLLECTIVE && (
            <FieldLayout
              label="Type de l’offre"
              name="collectiveOfferType"
              isOptional
            >
              <SelectInput
                onChange={storeCollectiveOfferType}
                disabled={disableAllFilters}
                name="collectiveOfferType"
                options={COLLECTIVE_OFFER_TYPES_OPTIONS}
                value={selectedFilters.collectiveOfferType}
              />
            </FieldLayout>
          )}
          <fieldset>
            <legend>Période de l’évènement</legend>

            <PeriodSelector
              onBeginningDateChange={onBeginningDateChange}
              onEndingDateChange={onEndingDateChange}
              isDisabled={disableAllFilters}
              periodBeginningDate={selectedFilters.periodBeginningDate}
              periodEndingDate={selectedFilters.periodEndingDate}
            />
          </fieldset>
        </FormLayout.Row>

        <div className={styles['reset-filters']}>
          <Button
            icon={fullRefreshIcon}
            disabled={!hasSearchFilters(selectedFilters)}
            onClick={resetFilters}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </Button>
        </div>
        <div className={styles['search-separator']}>
          <div className={styles['separator']} />
          <SubmitButton disabled={disableAllFilters}>Rechercher</SubmitButton>
          <div className={styles['separator']} />
        </div>
      </form>
    </>
  )
}

export default SearchFilters
