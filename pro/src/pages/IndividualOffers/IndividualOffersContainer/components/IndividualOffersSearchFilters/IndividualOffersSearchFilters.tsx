import type { ChangeEvent, Dispatch, FormEvent, SetStateAction } from 'react'

import { OfferStatus } from '@/apiClient/v1'
import {
  ALL_CATEGORIES_OPTION,
  ALL_OFFERER_ADDRESS_OPTION,
  ALL_STATUS,
  CREATION_MODES_OPTIONS,
  DEFAULT_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import type { IndividualSearchFiltersParams } from '@/commons/core/Offers/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OffersTableSearch } from '@/components/OffersTableSearch/OffersTableSearch'
import styles from '@/components/OffersTableSearch/OffersTableSearch.module.scss'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

interface IndividualOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: IndividualSearchFiltersParams) => void
  selectedFilters: IndividualSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<IndividualSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  offererAddresses: SelectOption[]
  categories?: SelectOption[]
  searchButtonRef?: React.RefObject<HTMLButtonElement>
}

const individualFilterStatus = [
  { label: 'Tous', value: ALL_STATUS },
  { label: 'Brouillon', value: OfferStatus.DRAFT },
  { label: 'Publiée', value: OfferStatus.ACTIVE },
  { label: 'Programmée', value: OfferStatus.SCHEDULED },
  { label: 'En pause', value: OfferStatus.INACTIVE },
  { label: 'Épuisée', value: OfferStatus.SOLD_OUT },
  { label: 'Expirée', value: OfferStatus.EXPIRED },
  { label: 'En instruction', value: OfferStatus.PENDING },
  { label: 'Non conforme', value: OfferStatus.REJECTED },
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
  searchButtonRef,
}: IndividualOffersSearchFiltersProps): JSX.Element => {
  const updateSearchFilters = (
    patch: Partial<IndividualSearchFiltersParams>
  ) => {
    setSelectedFilters((prev: IndividualSearchFiltersParams) => ({
      ...prev,
      ...patch,
    }))
  }

  // ONE generic change handler for text/select inputs.
  const handleChange = (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = event.currentTarget
    // Cast is safe because we align `name` with keys of SearchFiltersParams
    updateSearchFilters({
      [name]: value,
    } as Partial<IndividualSearchFiltersParams>)
  }

  // Tiny helper for dates to keep the single point of update logic.
  const handleDateChange =
    (key: 'periodBeginningDate' | 'periodEndingDate') => (val: string) => {
      const fallback =
        key === 'periodBeginningDate'
          ? DEFAULT_SEARCH_FILTERS.periodBeginningDate
          : DEFAULT_SEARCH_FILTERS.periodEndingDate
      updateSearchFilters({ [key]: val !== '' ? val : fallback })
    }

  const requestFilteredOffers = (event: FormEvent) => {
    event.preventDefault()
    applyFilters(selectedFilters)
  }

  return (
    <OffersTableSearch
      type="individual"
      hasActiveFilters={hasFilters}
      onSubmit={requestFilteredOffers}
      isDisabled={disableAllFilters}
      nameInputProps={{
        label: 'Nom de l’offre ou EAN-13 (European Article Numbering)',
        disabled: disableAllFilters,
        onChange: handleChange,
        value: selectedFilters.nameOrIsbn,
      }}
      onResetFilters={resetFilters}
      searchButtonRef={searchButtonRef}
    >
      <FormLayout.Row inline>
        <FieldLayout label="Statut" name="status" required={false}>
          <SelectInput
            value={selectedFilters.status as OfferStatus}
            name="status"
            onChange={handleChange}
            disabled={disableAllFilters}
            options={individualFilterStatus}
          />
        </FieldLayout>

        <FieldLayout
          label="Localisation"
          name="offererAddressId"
          required={false}
        >
          <SelectInput
            defaultOption={ALL_OFFERER_ADDRESS_OPTION}
            onChange={handleChange}
            disabled={offererAddresses.length === 0 || disableAllFilters}
            name="offererAddressId"
            options={offererAddresses}
            data-testid="address-select"
            value={selectedFilters.offererAddressId}
          />
        </FieldLayout>

        {categories && (
          <FieldLayout label="Catégorie" name="categoryId" required={false}>
            <SelectInput
              defaultOption={ALL_CATEGORIES_OPTION}
              onChange={handleChange}
              disabled={disableAllFilters}
              name="categoryId"
              options={categories}
              value={selectedFilters.categoryId}
            />
          </FieldLayout>
        )}

        <FieldLayout
          label="Mode de création"
          name="creationMode"
          hasLabelLineBreak={false}
          required={false}
        >
          <SelectInput
            onChange={handleChange}
            disabled={disableAllFilters}
            name="creationMode"
            options={CREATION_MODES_OPTIONS}
            value={selectedFilters.creationMode}
          />
        </FieldLayout>

        <FieldLayout
          label="Période de l’évènement"
          name="period"
          required={false}
          className={styles['offers-table-search-filter-full-width']}
        >
          <PeriodSelector
            onBeginningDateChange={handleDateChange('periodBeginningDate')}
            onEndingDateChange={handleDateChange('periodEndingDate')}
            isDisabled={disableAllFilters}
            periodBeginningDate={selectedFilters.periodBeginningDate}
            periodEndingDate={selectedFilters.periodEndingDate}
          />
        </FieldLayout>
      </FormLayout.Row>
    </OffersTableSearch>
  )
}
