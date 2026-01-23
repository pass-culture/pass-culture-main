import type { Dispatch, FormEvent, SetStateAction } from 'react'

import { CollectiveOfferDisplayedStatus, EacFormat } from '@/apiClient/v1'
import {
  ALL_FORMATS_OPTION,
  DEFAULT_COLLECTIVE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OffersTableSearch } from '@/components/OffersTableSearch/OffersTableSearch'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './AdminCollectiveOffersSearchFilters.module.scss'

export interface AdminCollectiveOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offererId: string | undefined
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  searchButtonRef?: React.RefObject<HTMLButtonElement>
}

export const AdminCollectiveOffersSearchFilters = ({
  hasFilters,
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  offererId,
  disableAllFilters,
  searchButtonRef,
}: AdminCollectiveOffersSearchFiltersProps): JSX.Element => {
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

  const {
    periodBeginningDate: defaultPeriodBeginningDate,
    periodEndingDate: defaultPeriodEndingDate,
  } = DEFAULT_COLLECTIVE_SEARCH_FILTERS

  const onBeginningDateChange = (periodBeginningDate: string) => {
    const dateToFilter =
      periodBeginningDate !== ''
        ? periodBeginningDate
        : defaultPeriodBeginningDate
    updateSearchFilters({ periodBeginningDate: dateToFilter })
  }

  const onEndingDateChange = (periodEndingDate: string) => {
    const dateToFilter =
      periodEndingDate !== '' ? periodEndingDate : defaultPeriodEndingDate
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

  const collectiveFilterStatus = [
    {
      id: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
      label: 'En instruction',
    },
    {
      id: CollectiveOfferDisplayedStatus.REJECTED,
      label: 'Non conforme',
    },
    {
      id: CollectiveOfferDisplayedStatus.PUBLISHED,
      label: 'Publiée sur ADAGE',
    },
    {
      id: CollectiveOfferDisplayedStatus.PREBOOKED,
      label: 'Préréservée',
    },
    {
      id: CollectiveOfferDisplayedStatus.BOOKED,
      label: 'Réservée',
    },
    {
      id: CollectiveOfferDisplayedStatus.EXPIRED,
      label: 'Expirée',
    },
    {
      id: CollectiveOfferDisplayedStatus.ENDED,
      label: 'Terminée',
    },
    {
      id: CollectiveOfferDisplayedStatus.ARCHIVED,
      label: 'Archivée',
    },
    {
      id: CollectiveOfferDisplayedStatus.DRAFT,
      label: 'Brouillon',
    },
    {
      id: CollectiveOfferDisplayedStatus.REIMBURSED,
      label: 'Remboursée',
    },
    {
      id: CollectiveOfferDisplayedStatus.CANCELLED,
      label: 'Annulée',
    },
  ]

  const onResetFilters = () => {
    resetFilters()
  }

  return (
    <OffersTableSearch
      type="collective"
      onSubmit={requestFilteredOffers}
      isDisabled={disableAllFilters}
      hasActiveFilters={hasFilters}
      nameInputProps={{
        label: 'Nom de l’offre',
        disabled: disableAllFilters,
        onChange: (event) =>
          updateSearchFilters({ name: event.currentTarget.value }),
        value: selectedFilters.name,
      }}
      onResetFilters={onResetFilters}
      searchButtonRef={searchButtonRef}
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
          defaultOption={ALL_FORMATS_OPTION}
          onChange={(event) =>
            updateSearchFilters({
              format: event.currentTarget.value as EacFormat | 'all',
            })
          }
          disabled={disableAllFilters}
          name="format"
          options={formats}
          value={selectedFilters.format}
          label="Format"
        />
      </FormLayout.Row>
      <FieldLayout
        label="Période de l'évènement"
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
