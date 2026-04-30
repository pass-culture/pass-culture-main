import type { ChangeEvent, Dispatch, SetStateAction, SubmitEvent } from 'react'

import { OfferStatus } from '@/apiClient/v1'
import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import type { SearchListParams } from '@/commons/core/Offers/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OffersTableSearch } from '@/components/OffersTableSearch/OffersTableSearch'
import { TypedSelect } from '@/components/TypedSelect/TypedSelect'
import styles from '@/pages/IndividualOffers/IndividualOffersContainer/IndividualOffersContainer.module.scss'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'

type IndividualFilterShape = ListOffersQueryModel & SearchListParams

interface IndividualOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: IndividualFilterShape) => void
  selectedFilters: IndividualFilterShape
  setSelectedFilters: Dispatch<SetStateAction<IndividualFilterShape>>
  disableAllFilters: boolean
  resetFilters: () => void
  offererAddresses: SelectOption<number>[]
  categories?: SelectOption[]
  searchButtonRef?: React.RefObject<HTMLButtonElement | null>
}

const individualFilterStatus: SelectOption[] = [
  { label: 'Brouillon', value: OfferStatus.DRAFT },
  { label: 'Publiée', value: OfferStatus.ACTIVE },
  { label: 'Programmée', value: OfferStatus.SCHEDULED },
  { label: 'En pause', value: OfferStatus.INACTIVE },
  { label: 'Épuisée', value: OfferStatus.SOLD_OUT },
  { label: 'Expirée', value: OfferStatus.EXPIRED },
  { label: 'En instruction', value: OfferStatus.PENDING },
  { label: 'Non conforme', value: OfferStatus.REJECTED },
]

const creationModeOptions: SelectOption[] = [
  { label: 'Manuel', value: 'manual' },
  { label: 'Synchronisé', value: 'imported' },
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
}: Readonly<IndividualOffersSearchFiltersProps>) => {
  const updateSearchFilters = (patch: Partial<IndividualFilterShape>) => {
    setSelectedFilters((prev) => ({ ...prev, ...patch }))
  }

  const handleNameChange = (event: ChangeEvent<HTMLInputElement>) => {
    updateSearchFilters({ nameOrIsbn: event.currentTarget.value })
  }

  const handleDateChange =
    (key: 'periodBeginningDate' | 'periodEndingDate') => (val: string) => {
      const fallback =
        key === 'periodBeginningDate'
          ? DEFAULT_SEARCH_FILTERS.periodBeginningDate
          : DEFAULT_SEARCH_FILTERS.periodEndingDate
      updateSearchFilters({ [key]: val !== '' ? val : fallback })
    }

  const requestFilteredOffers = (event: SubmitEvent<HTMLFormElement>) => {
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
        onChange: handleNameChange,
        value: selectedFilters.nameOrIsbn ?? '',
      }}
      onResetFilters={resetFilters}
      searchButtonRef={searchButtonRef}
    >
      <FormLayout.Row inline mdSpaceAfter>
        <TypedSelect
          label="Statut"
          name="status"
          emptyOptionLabel="Tous"
          options={individualFilterStatus}
          value={selectedFilters.status}
          onChange={(value) =>
            updateSearchFilters({ status: value as OfferStatus | undefined })
          }
          disabled={disableAllFilters}
          className={styles['select-filter']}
        />

        <TypedSelect
          label="Localisation"
          name="offererAddressId"
          emptyOptionLabel="Toutes"
          isNumber
          options={offererAddresses}
          value={selectedFilters.offererAddressId}
          onChange={(value) => updateSearchFilters({ offererAddressId: value })}
          disabled={offererAddresses.length === 0 || disableAllFilters}
          className={styles['select-filter']}
        />

        {categories && (
          <TypedSelect
            label="Catégorie"
            name="categoryId"
            emptyOptionLabel="Toutes"
            options={categories}
            value={selectedFilters.categoryId}
            onChange={(value) => updateSearchFilters({ categoryId: value })}
            disabled={disableAllFilters}
            className={styles['select-filter']}
          />
        )}

        <TypedSelect
          label="Mode de création"
          name="creationMode"
          emptyOptionLabel="Tous"
          options={creationModeOptions}
          value={selectedFilters.creationMode}
          onChange={(value) => updateSearchFilters({ creationMode: value })}
          disabled={disableAllFilters}
          className={styles['select-filter']}
        />
      </FormLayout.Row>

      <FormLayout.Row mdSpaceAfter>
        <PeriodSelector
          legend="Période de l’évènement"
          onBeginningDateChange={handleDateChange('periodBeginningDate')}
          onEndingDateChange={handleDateChange('periodEndingDate')}
          isDisabled={disableAllFilters}
          periodBeginningDate={selectedFilters.periodBeginningDate ?? ''}
          periodEndingDate={selectedFilters.periodEndingDate ?? ''}
        />
      </FormLayout.Row>
    </OffersTableSearch>
  )
}
