import { FormikProvider, useFormik } from 'formik'
import { Dispatch, FormEvent, SetStateAction, useEffect } from 'react'

import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  ALL_FORMATS_OPTION,
  ALL_STRUCTURES_OPTION,
  ALL_VENUES_OPTION,
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
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

interface CollectiveOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offerer: GetOffererResponseModel | null
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
  categories?: SelectOption[]
}

const collectiveFilterStatus = [
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
  {
    label: 'Brouillon',
    value: CollectiveOfferDisplayedStatus.DRAFT,
  },
]

type StatusFormValues = {
  status: CollectiveOfferDisplayedStatus[]
  'search-status': string
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
}: CollectiveOffersSearchFiltersProps): JSX.Element => {
  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )
  const areCollectiveNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )
  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  const defaultCollectiveFilters = useDefaultCollectiveSearchFilters()

  const formats: SelectOption[] = Object.values(EacFormat).map((format) => ({
    value: format,
    label: format,
  }))

  const formik = useFormik<StatusFormValues>({
    initialValues: {
      status: Array.isArray(selectedFilters.status)
        ? selectedFilters.status
        : [selectedFilters.status],
      'search-status': '',
    },
    onSubmit: () => {},
  })

  // TODO(anoukhello - 24/07/24) we should not use useEffect for this but an event handler on SelectAutocomplete
  useEffect(() => {
    updateSearchFilters({ status: formik.values.status })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formik.values.status])

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

  const storeSelectedVenue = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({ venueId: event.currentTarget.value })
  }

  const storeSelectedFormat = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({
      format: event.currentTarget.value as EacFormat | 'all',
    })
  }

  const storeCollectiveOfferType = (event: FormEvent<HTMLSelectElement>) => {
    updateSearchFilters({
      collectiveOfferType: event.currentTarget.value as CollectiveOfferTypeEnum,
    })
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

  const onResetFilters = async () => {
    await formik.setFieldValue('status', defaultCollectiveFilters.status)
    resetFilters()
  }

  const searchByOfferNameLabel = 'Nom de l’offre'

  const statusFilterOptions = [
    ...collectiveFilterStatus
      .filter(
        (status) =>
          !isNewOffersAndBookingsActive ||
          status.value !== CollectiveOfferDisplayedStatus.INACTIVE
      )
      .map((status) => {
        if (areCollectiveNewStatusesEnabled) {
          if (status.value === CollectiveOfferDisplayedStatus.PENDING) {
            return { ...status, label: 'En instruction' }
          }
          if (status.value === CollectiveOfferDisplayedStatus.REJECTED) {
            return { ...status, label: 'Non conforme' }
          }
          if (status.value === CollectiveOfferDisplayedStatus.INACTIVE) {
            return { ...status, label: 'En pause' }
          }
        }
        return status
      }),
    ...(areCollectiveNewStatusesEnabled
      ? [
          {
            label: 'Remboursée',
            value: CollectiveOfferDisplayedStatus.REIMBURSED,
          },
          {
            label: 'Annulée',
            value: CollectiveOfferDisplayedStatus.CANCELLED,
          },
        ]
      : []),
  ]

  return (
    <OffersTableSearch
      type="collective"
      onSubmit={requestFilteredOffers}
      isDisabled={disableAllFilters}
      hasActiveFilters={hasFilters}
      nameInputProps={{
        label: searchByOfferNameLabel,
        disabled: disableAllFilters,
        onChange: storeNameOrIsbnSearchValue,
        value: selectedFilters.nameOrIsbn,
      }}
      onResetFilters={onResetFilters}
    >
      <FormLayout.Row inline>
        <FormikProvider value={formik}>
          <SelectAutocomplete
            multi
            name="status"
            label="Statut"
            options={statusFilterOptions}
            isOptional
            disabled={disableAllFilters}
          />
        </FormikProvider>
        <FieldLayout
          label={isOfferAddressEnabled ? 'Structure' : 'Lieu'}
          name="lieu"
          isOptional
        >
          <SelectInput
            defaultOption={
              isOfferAddressEnabled ? ALL_STRUCTURES_OPTION : ALL_VENUES_OPTION
            }
            onChange={storeSelectedVenue}
            disabled={disableAllFilters}
            name="lieu"
            options={venues}
            value={selectedFilters.venueId}
          />
        </FieldLayout>
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
        {!isNewOffersAndBookingsActive && (
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
