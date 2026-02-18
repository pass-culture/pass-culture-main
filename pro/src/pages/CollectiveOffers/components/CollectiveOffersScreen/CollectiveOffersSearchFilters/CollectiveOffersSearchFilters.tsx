import type { Dispatch, SetStateAction, SubmitEvent } from 'react'

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
import { OffersTableFilterBar } from '@/components/OffersTableFilterBar/OffersTableFilterBar'
import { OffersTableSearch } from '@/components/OffersTableSearch/OffersTableSearch'
import { formatAndOrderAddresses } from '@/repository/venuesService'
import { MultiSelect } from '@/ui-kit/form/MultiSelect/MultiSelect'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from '../CollectiveOffersScreen.module.scss'

export interface CollectiveOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters?: (filters: CollectiveSearchFiltersParams) => void
  offererId: string | undefined
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters?: boolean
  isAdministrationSpace?: boolean
  resetFilters: () => void
  searchButtonRef?: React.RefObject<HTMLButtonElement | null>
}

export const CollectiveOffersSearchFilters = ({
  hasFilters,
  applyFilters,
  selectedFilters,
  isAdministrationSpace = false,
  setSelectedFilters,
  resetFilters,
  offererId,
  disableAllFilters = false,
  searchButtonRef,
}: Readonly<CollectiveOffersSearchFiltersProps>): JSX.Element => {
  const offererAddressQuery = useOffererAddresses(
    GetOffererAddressesWithOffersOption.COLLECTIVE_OFFERS_ONLY
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
      ...address,
      value: address.value,
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

  const requestFilteredOffers = (event: SubmitEvent<HTMLFormElement>) => {
    event.preventDefault()
    const newSearchFilters = {
      ...selectedFilters,
      offererId: offererId?.toString() ?? '',
    }

    applyFilters?.(newSearchFilters)
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

  const children = (
    <>
      <FormLayout.Row inline mdSpaceAfter>
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
        {!isAdministrationSpace && (
          <Select
            className={styles['filter-container']}
            defaultOption={ALL_OFFERER_ADDRESS_OPTION}
            onChange={(event) =>
              handleLocationChange(event.currentTarget.value)
            }
            disabled={disableAllFilters}
            name="location"
            options={locationOptions}
            value={
              selectedFilters.offererAddressId !== undefined &&
              selectedFilters.offererAddressId !== null
                ? String(selectedFilters.offererAddressId)
                : selectedFilters.locationType !== undefined &&
                    selectedFilters.locationType !== null
                  ? String(selectedFilters.locationType)
                  : 'all'
            }
            label="Localisation"
          />
        )}
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
      <FormLayout.Row mdSpaceAfter>
        <PeriodSelector
          legend="Période de l’évènement"
          onBeginningDateChange={onBeginningDateChange}
          onEndingDateChange={onEndingDateChange}
          isDisabled={disableAllFilters}
          periodBeginningDate={selectedFilters.periodBeginningDate}
          periodEndingDate={selectedFilters.periodEndingDate}
        />
      </FormLayout.Row>
    </>
  )

  if (isAdministrationSpace) {
    return (
      <OffersTableFilterBar
        isDisabled={disableAllFilters}
        isInline
        onReset={resetFilters}
      >
        {children}
      </OffersTableFilterBar>
    )
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
      onResetFilters={resetFilters}
      searchButtonRef={searchButtonRef}
    >
      {children}
    </OffersTableSearch>
  )
}
