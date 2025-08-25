import type { Dispatch, FormEvent, SetStateAction } from 'react'

import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  type GetOffererResponseModel,
} from '@/apiClient/v1'
import {
  ALL_FORMATS_OPTION,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'
import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { OffersTableSearch } from '@/components/OffersTable/OffersTableSearch/OffersTableSearch'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from '../TemplateCollectiveOffersScreen.module.scss'

interface TemplateOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offerer: GetOffererResponseModel | null
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
  offerer,
  disableAllFilters,
}: TemplateOffersSearchFiltersProps): JSX.Element => {
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
    updateSearchFilters({ nameOrIsbn: event.currentTarget.value })
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
        : DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.periodBeginningDate
    updateSearchFilters({ periodBeginningDate: dateToFilter })
  }

  const onEndingDateChange = (periodEndingDate: string) => {
    const dateToFilter =
      periodEndingDate !== ''
        ? periodEndingDate
        : DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.periodEndingDate
    updateSearchFilters({ periodEndingDate: dateToFilter })
  }

  const requestFilteredOffers = (event: FormEvent) => {
    event.preventDefault()
    const newSearchFilters = {
      ...selectedFilters,
      offererId: offerer?.id.toString() ?? '',
    }

    applyFilters(newSearchFilters)
  }

  const resetCollectiveFilters = () => {
    resetFilters()
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
        value: selectedFilters.nameOrIsbn,
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
            searchLabel="Rechercher"
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
          onChange={storeSelectedFormat}
          disabled={disableAllFilters}
          name="format"
          label="Format"
          options={formats}
          value={selectedFilters.format}
        />
        <FieldLayout label="Période de l’évènement" name="period" isOptional>
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
