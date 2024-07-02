import { Dispatch, FormEvent, SetStateAction } from 'react'

import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  GetOffererResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  ALL_CATEGORIES_OPTION,
  ALL_FORMATS_OPTION,
  ALL_STATUS,
  ALL_VENUES_OPTION,
  COLLECTIVE_OFFER_TYPES_OPTIONS,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { hasSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { Audience } from 'core/shared/types'
import { SelectOption } from 'custom_types/form'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './SearchFilters.module.scss'

interface SearchFiltersProps {
  applyFilters: (filters: SearchFiltersParams) => void
  offerer: GetOffererResponseModel | null
  removeOfferer: () => void
  selectedFilters: SearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<SearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
  categories?: SelectOption[]
  audience: Audience
  isRestrictedAsAdmin?: boolean
}

const collectiveFilterStatus = [
  { label: 'Tous', value: ALL_STATUS },
  {
    label: 'Validation en attente',
    value: CollectiveOfferDisplayedStatus.PENDING,
  },
  {
    label: 'Refusée',
    value: CollectiveOfferDisplayedStatus.REJECTED,
  },
  { label: 'Publiée sur ADAGE', value: CollectiveOfferDisplayedStatus.ACTIVE },
  {
    label: 'Masquée sur ADAGE',
    value: CollectiveOfferDisplayedStatus.INACTIVE,
  },
  { label: 'Préréservée', value: CollectiveOfferDisplayedStatus.PREBOOKED },
  {
    label: 'Réservée',
    value: CollectiveOfferDisplayedStatus.BOOKED,
  },
  { label: 'Expirée', value: CollectiveOfferDisplayedStatus.EXPIRED },
  { label: 'Terminée', value: CollectiveOfferDisplayedStatus.ENDED },
  { label: 'Archivée', value: CollectiveOfferDisplayedStatus.ARCHIVED },
]

const individualFilterStatus = [
  { label: 'Tous', value: ALL_STATUS },
  { label: 'Brouillon', value: OfferStatus.DRAFT },
  { label: 'Publiée', value: OfferStatus.ACTIVE },
  { label: 'Désactivée', value: OfferStatus.INACTIVE },
  { label: 'Épuisée', value: OfferStatus.SOLD_OUT },
  { label: 'Expirée', value: OfferStatus.EXPIRED },
  { label: 'Validation en attente', value: OfferStatus.PENDING },
  { label: 'Refusée', value: OfferStatus.REJECTED },
]

export const SearchFilters = ({
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  offerer,
  removeOfferer,
  disableAllFilters,
  venues,
  categories,
  audience,
  isRestrictedAsAdmin = false,
}: SearchFiltersProps): JSX.Element => {
  const isNewInterfaceActive = useIsNewInterfaceActive()
  const formats: SelectOption[] = Object.values(EacFormat).map((format) => ({
    value: format,
    label: format,
  }))

  const updateSearchFilters = (
    newSearchFilters: Partial<SearchFiltersParams>
  ) => {
    setSelectedFilters((currentSearchFilters) => ({
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

  const storeOfferStatus = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ status: event.currentTarget.value as OfferStatus })
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
    applyFilters(selectedFilters)
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
          {!isNewInterfaceActive && (
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
          )}
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

          {audience === Audience.COLLECTIVE ? (
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
            categories && (
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
            )
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
        <FieldLayout
          label={
            <span className={styles['status-filter-label']}>
              Statut<Tag variant={TagVariant.BLUE}>Nouveau</Tag>
            </span>
          }
          name="status"
          isOptional
          className={styles['status-filter']}
        >
          <SelectInput
            value={selectedFilters.status}
            name="status"
            onChange={storeOfferStatus}
            disabled={disableAllFilters || isRestrictedAsAdmin}
            options={
              audience === Audience.COLLECTIVE
                ? collectiveFilterStatus
                : individualFilterStatus
            }
          />
        </FieldLayout>

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
          <Button type="submit" disabled={disableAllFilters}>
            Rechercher
          </Button>
          <div className={styles['separator']} />
        </div>
      </form>
    </>
  )
}
