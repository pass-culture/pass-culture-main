import { Dispatch, FormEvent, SetStateAction } from 'react'

import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  ALL_FORMATS_OPTION,
  ALL_OFFERERS_OPTION,
  COLLECTIVE_OFFER_TYPES_OPTIONS,
} from 'commons/core/Offers/constants'
import { useDefaultCollectiveSearchFilters } from 'commons/core/Offers/hooks/useDefaultCollectiveSearchFilters'
import {
  CollectiveOfferTypeEnum,
  CollectiveSearchFiltersParams,
} from 'commons/core/Offers/types'
import { SelectOption } from 'commons/custom_types/form'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { OffersTableSearch } from 'components/OffersTable/OffersTableSearch/OffersTableSearch'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { Select } from 'ui-kit/formV2/Select/Select'
import { MultiSelect } from 'ui-kit/MultiSelect/MultiSelect'

import styles from '../CollectiveOffersScreen.module.scss'

interface CollectiveOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offerer: GetOffererResponseModel | null
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
  searchButtonRef?: React.RefObject<HTMLButtonElement>
}

export const CollectiveOffersSearchFilters = ({
  hasFilters,
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  offerer,
  disableAllFilters,
  venues,
  searchButtonRef,
}: CollectiveOffersSearchFiltersProps): JSX.Element => {
  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()

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

  const onBeginningDateChange = (periodBeginningDate: string) => {
    const dateToFilter =
      periodBeginningDate !== ''
        ? periodBeginningDate
        : defaultCollectiveFilters.periodBeginningDate
    updateSearchFilters({ periodBeginningDate: dateToFilter })
  }

  const onEndingDateChange = (periodEndingDate: string) => {
    const dateToFilter =
      periodEndingDate !== ''
        ? periodEndingDate
        : defaultCollectiveFilters.periodEndingDate
    updateSearchFilters({ periodEndingDate: dateToFilter })
  }

  const requestFilteredOffers = (event: FormEvent) => {
    event.preventDefault()
    const newSearchFilters = {
      ...selectedFilters,
      offererId: offerer?.id.toString() ?? 'all',
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
    ...(!isNewOffersAndBookingsActive
      ? [
          {
            id: CollectiveOfferDisplayedStatus.HIDDEN,
            label: 'En pause',
          },
        ]
      : []),
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
          updateSearchFilters({ nameOrIsbn: event.currentTarget.value }),
        value: selectedFilters.nameOrIsbn,
      }}
      onResetFilters={onResetFilters}
      searchButtonRef={searchButtonRef}
    >
      <FormLayout.Row inline mdSpaceAfter>
        <div className={styles['offer-multiselect-status']}>
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
          defaultOption={ALL_OFFERERS_OPTION}
          onChange={(event) =>
            updateSearchFilters({ venueId: event.currentTarget.value })
          }
          disabled={disableAllFilters}
          name="structure"
          options={venues}
          value={selectedFilters.venueId}
          label="Structure"
        />
        <Select
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
        {!isNewOffersAndBookingsActive && (
          <Select
            onChange={(event) =>
              updateSearchFilters({
                collectiveOfferType: event.currentTarget
                  .value as CollectiveOfferTypeEnum,
              })
            }
            disabled={disableAllFilters}
            name="collectiveOfferType"
            options={COLLECTIVE_OFFER_TYPES_OPTIONS}
            value={selectedFilters.collectiveOfferType}
            label="Type de l’offre"
          />
        )}
      </FormLayout.Row>
      <FieldLayout label="Période de l’évènement" name="period" isOptional>
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
