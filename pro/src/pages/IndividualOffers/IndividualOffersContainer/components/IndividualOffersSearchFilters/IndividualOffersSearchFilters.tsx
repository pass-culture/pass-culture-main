import { Dispatch, FormEvent, SetStateAction } from 'react'

import { OfferStatus } from 'apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  ALL_OFFERER_ADDRESS_OPTION,
  ALL_STATUS,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OffersTableSearch } from 'components/OffersTable/OffersTableSearch/OffersTableSearch'
import styles from 'components/OffersTable/OffersTableSearch/OffersTableSearch.module.scss'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

interface IndividualOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: SearchFiltersParams) => void
  selectedFilters: SearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<SearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  offererAddresses: SelectOption[]
  categories?: SelectOption[]
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
  hasFilters,
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  disableAllFilters,
  offererAddresses,
  categories,
}: IndividualOffersSearchFiltersProps): JSX.Element => {
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
    <OffersTableSearch
      type="individual"
      hasActiveFilters={hasFilters}
      onSubmit={requestFilteredOffers}
      isDisabled={disableAllFilters}
      nameInputProps={{
        label: searchByOfferNameLabel,
        disabled: disableAllFilters,
        onChange: storeNameOrIsbnSearchValue,
        value: selectedFilters.nameOrIsbn,
      }}
      onResetFilters={resetFilters}
    >
      <FormLayout.Row inline>
        <FieldLayout label="Statut" name="status" isOptional>
          <SelectInput
            value={selectedFilters.status as OfferStatus}
            name="status"
            onChange={storeOfferStatus}
            disabled={disableAllFilters}
            options={statusFilterOptions}
          />
        </FieldLayout>
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
          hasLabelLineBreak={false}
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
        <FieldLayout
          label="Période de l’évènement"
          name="period"
          isOptional
          className={styles['offers-table-search-filter-full-width']}
        >
          <PeriodSelector
            onBeginningDateChange={onBeginningDateChange}
            onEndingDateChange={onEndingDateChange}
            isDisabled={disableAllFilters}
            periodBeginningDate={selectedFilters.periodBeginningDate}
            periodEndingDate={selectedFilters.periodEndingDate}
          />
        </FieldLayout>
      </FormLayout.Row>
    </OffersTableSearch>
  )
}
