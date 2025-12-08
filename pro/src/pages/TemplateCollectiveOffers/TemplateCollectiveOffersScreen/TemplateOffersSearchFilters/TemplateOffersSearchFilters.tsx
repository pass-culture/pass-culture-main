import type { Dispatch, FormEvent, SetStateAction } from 'react'

import {
  CollectiveLocationType,
  CollectiveOfferDisplayedStatus,
  EacFormat,
  GetOffererAddressesWithOffersOption,
} from '@/apiClient/v1'
import {
  ALL_FORMATS_OPTION,
  ALL_OFFERER_ADDRESS_OPTION,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { useOffererAddresses } from '@/commons/hooks/swr/useOffererAddresses'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OffersTableSearch } from '@/components/OffersTableSearch/OffersTableSearch'
import { formatAndOrderAddresses } from '@/repository/venuesService'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from '../TemplateCollectiveOffersScreen.module.scss'

interface TemplateOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offererId: string | undefined
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
}

const collectiveFilterStatus = [
  {
    label: 'En instruction',
    id: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
  },
  {
    label: 'Non conforme',
    id: CollectiveOfferDisplayedStatus.REJECTED,
  },
  {
    label: 'Publiée sur ADAGE',
    id: CollectiveOfferDisplayedStatus.PUBLISHED,
  },
  {
    label: 'En pause',
    id: CollectiveOfferDisplayedStatus.HIDDEN,
  },
  { label: 'Archivée', id: CollectiveOfferDisplayedStatus.ARCHIVED },
  {
    label: 'Brouillon',
    id: CollectiveOfferDisplayedStatus.DRAFT,
  },
  {
    label: 'Terminée',
    id: CollectiveOfferDisplayedStatus.ENDED,
  },
]

export const TemplateOffersSearchFilters = ({
  hasFilters,
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  offererId,
  disableAllFilters,
}: TemplateOffersSearchFiltersProps): JSX.Element => {
  const offererAddressQuery = useOffererAddresses(
    GetOffererAddressesWithOffersOption.COLLECTIVE_OFFER_TEMPLATES_ONLY
  )
  const offererAddresses = formatAndOrderAddresses(offererAddressQuery.data)

  const locationOptions = [
    {
      value: CollectiveLocationType.TO_BE_DEFINED,
      label: 'À déterminer',
    },
    {
      value: CollectiveLocationType.SCHOOL,
      label: 'En établissement scolaire',
    },
    ...offererAddresses.map((address) => ({
      value: address.value,
      label: address.label,
    })),
  ]

  const formats: SelectOption[] = Object.values(EacFormat).map((format) => ({
    value: format,
    label: format,
  }))

  const updateSearchFilters = (
    newSearchFilters: Partial<CollectiveSearchFiltersParams>
  ) => {
    setSelectedFilters((currentSearchFilters) => ({
      ...currentSearchFilters,
      ...newSearchFilters,
    }))
  }

  const storeNameOrIsbnSearchValue = (event: FormEvent<HTMLInputElement>) => {
    updateSearchFilters({ name: event.currentTarget.value })
  }

  const storeSelectedFormat = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({
      format: event.currentTarget.value as EacFormat | 'all',
    })
  }

  const onBeginningDateChange = (periodBeginningDate: string) => {
    const dateToFilter =
      periodBeginningDate !== ''
        ? periodBeginningDate
        : DEFAULT_COLLECTIVE_SEARCH_FILTERS.periodBeginningDate
    updateSearchFilters({ periodBeginningDate: dateToFilter })
  }

  const onEndingDateChange = (periodEndingDate: string) => {
    const dateToFilter =
      periodEndingDate !== ''
        ? periodEndingDate
        : DEFAULT_COLLECTIVE_SEARCH_FILTERS.periodEndingDate
    updateSearchFilters({ periodEndingDate: dateToFilter })
  }

  const requestFilteredOffers = (event: FormEvent) => {
    event.preventDefault()
    const newSearchFilters = {
      ...selectedFilters,
      offererId: offererId?.toString() ?? '',
    }

    applyFilters(newSearchFilters)
  }

  const resetCollectiveFilters = () => {
    resetFilters()
  }

  const handleLocationChange = (value: string) => {
    switch (value) {
      case CollectiveLocationType.TO_BE_DEFINED:
        updateSearchFilters({
          locationType: CollectiveLocationType.TO_BE_DEFINED,
          offererAddressId: undefined,
        })
        break
      case CollectiveLocationType.SCHOOL:
        updateSearchFilters({
          locationType: CollectiveLocationType.SCHOOL,
          offererAddressId: undefined,
        })
        break
      case 'all':
        updateSearchFilters({
          locationType: undefined,
          offererAddressId: undefined,
        })
        break
      default:
        updateSearchFilters({
          locationType: CollectiveLocationType.ADDRESS,
          offererAddressId: value,
        })
    }
  }

  return (
    <OffersTableSearch
      type="template"
      onSubmit={requestFilteredOffers}
      isDisabled={disableAllFilters}
      hasActiveFilters={hasFilters}
      nameInputProps={{
        label: 'Nom de l’offre',
        disabled: disableAllFilters,
        onChange: storeNameOrIsbnSearchValue,
        value: selectedFilters.name,
      }}
      onResetFilters={resetCollectiveFilters}
    >
      <FormLayout.Row inline smSpaceAfter>
        <div className={styles['filter-container']}>
          <MultiSelect
            name="status"
            label="Statut"
            options={collectiveFilterStatus}
            hasSearch
            searchLabel="Rechercher un statut"
            buttonLabel="Statut"
            onSelectedOptionsChanged={(selectedOptions) => {
              const selectedIds = selectedOptions.map(
                (option) => option.id as CollectiveOfferDisplayedStatus
              )

              updateSearchFilters({
                status: selectedIds,
              })
            }}
            disabled={disableAllFilters}
            selectedOptions={selectedFilters.status.map((option) => ({
              id: option,
              label:
                collectiveFilterStatus.find((op) => op.id === option)?.label ||
                '',
            }))}
          />
        </div>
        <Select
          className={styles['filter-container']}
          defaultOption={ALL_OFFERER_ADDRESS_OPTION}
          onChange={(event) => handleLocationChange(event.currentTarget.value)}
          disabled={disableAllFilters}
          name="location"
          options={locationOptions}
          value={
            selectedFilters.locationType ===
            CollectiveLocationType.TO_BE_DEFINED
              ? CollectiveLocationType.TO_BE_DEFINED
              : selectedFilters.locationType === CollectiveLocationType.SCHOOL
                ? CollectiveLocationType.SCHOOL
                : selectedFilters.offererAddressId != null
                  ? String(selectedFilters.offererAddressId)
                  : 'all'
          }
          label="Localisation"
        />
        <Select
          className={styles['filter-container']}
          defaultOption={ALL_FORMATS_OPTION}
          onChange={storeSelectedFormat}
          disabled={disableAllFilters}
          name="format"
          label="Format"
          options={formats}
          value={selectedFilters.format}
        />
      </FormLayout.Row>
      <FieldLayout
        label="Période de l’évènement"
        name="period"
        required={false}
      >
        <PeriodSelector
          onBeginningDateChange={onBeginningDateChange}
          onEndingDateChange={onEndingDateChange}
          isDisabled={disableAllFilters}
          periodBeginningDate={selectedFilters.periodBeginningDate}
          periodEndingDate={selectedFilters.periodEndingDate}
        />
      </FieldLayout>
    </OffersTableSearch>
  )
}
