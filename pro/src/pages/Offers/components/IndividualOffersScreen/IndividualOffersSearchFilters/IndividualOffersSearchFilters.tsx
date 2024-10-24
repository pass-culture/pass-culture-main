import { Dispatch, FormEvent, SetStateAction } from 'react'

import { OfferStatus } from 'apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  ALL_OFFERER_ADDRESS_OPTION,
  ALL_STATUS,
  ALL_VENUES_OPTION,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { hasSearchFilters } from 'commons/core/Offers/utils/hasSearchFilters'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './IndividualOffersSearchFilters.module.scss'

interface IndividualOffersSearchFiltersProps {
  applyFilters: (filters: SearchFiltersParams) => void
  selectedFilters: SearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<SearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
  offererAddresses: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
}

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

export const IndividualOffersSearchFilters = ({
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  disableAllFilters,
  venues,
  offererAddresses,
  categories,
  isRestrictedAsAdmin = false,
}: IndividualOffersSearchFiltersProps): JSX.Element => {
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  const areCollectiveNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )

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

  const storeSelectedOfferAddress = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ offererAddressId: event.currentTarget.value })
  }

  const storeSelectedCategory = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ categoryId: event.currentTarget.value })
  }

  const storeCreationMode = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ creationMode: event.currentTarget.value })
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

  const searchByOfferNameLabel = (
    <span>
      Nom de l’offre ou <abbr title="European Article Numbering">EAN-13</abbr>
    </span>
  )
  const searchByOfferNamePlaceholder =
    'Rechercher par nom d’offre ou par EAN-13'

  const statusFilterOptions = individualFilterStatus.map((status) => {
    if (areCollectiveNewStatusesEnabled) {
      if (status.value === OfferStatus.PENDING) {
        return { ...status, label: 'En instruction' }
      }
      if (status.value === OfferStatus.REJECTED) {
        return { ...status, label: 'Non conforme' }
      }
      if (status.value === OfferStatus.INACTIVE) {
        return { ...status, label: 'En pause' }
      }
    }
    return status
  })

  return (
    <>
      <form
        onSubmit={requestFilteredOffers}
        className={styles['search-filters-form']}
      >
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
          {isOfferAddressEnabled ? (
            <FieldLayout label="Localisation" name="address" isOptional>
              <SelectInput
                defaultOption={ALL_OFFERER_ADDRESS_OPTION}
                onChange={storeSelectedOfferAddress}
                disabled={offererAddresses.length === 0 || disableAllFilters}
                name="address"
                options={offererAddresses}
                data-testid="address-select"
                value={selectedFilters.offererAddressId}
              />
            </FieldLayout>
          ) : (
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
          )}

          {categories && (
            <FieldLayout label="Catégorie" name="categorie" isOptional>
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

          <FieldLayout
            label="Mode de création"
            name="creationMode"
            isOptional
            className={styles['filter-creation-mode']}
          >
            <SelectInput
              onChange={storeCreationMode}
              disabled={disableAllFilters}
              name="creationMode"
              options={CREATION_MODES_OPTIONS}
              value={selectedFilters.creationMode}
            />
          </FieldLayout>

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
        <FormLayout.Row inline className={styles['reset-filters-row']}>
          <FieldLayout
            label="Statut"
            name="status"
            isOptional
            className={styles['status-filter']}
          >
            <SelectInput
              value={selectedFilters.status as OfferStatus}
              name="status"
              onChange={storeOfferStatus}
              disabled={disableAllFilters || isRestrictedAsAdmin}
              options={statusFilterOptions}
            />
          </FieldLayout>
          <Button
            icon={fullRefreshIcon}
            disabled={!hasSearchFilters(selectedFilters)}
            onClick={resetFilters}
            variant={ButtonVariant.TERNARY}
            className={styles['reset-filters']}
          >
            Réinitialiser les filtres
          </Button>
        </FormLayout.Row>
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
