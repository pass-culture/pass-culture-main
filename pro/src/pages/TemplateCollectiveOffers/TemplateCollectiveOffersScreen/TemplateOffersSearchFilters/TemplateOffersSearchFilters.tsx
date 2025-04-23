import { FormikProvider, useFormik } from 'formik'
import { Dispatch, FormEvent, SetStateAction, useEffect } from 'react'

import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  GetOffererResponseModel,
} from 'apiClient/v1'
import {
  ALL_FORMATS_OPTION,
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
} from 'commons/core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { SelectOption } from 'commons/custom_types/form'
import { OffersTableSearch } from 'components/OffersTable/OffersTableSearch/OffersTableSearch'
import styles from 'components/OffersTable/OffersTableSearch/OffersTableSearch.module.scss'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

interface TemplateOffersSearchFiltersProps {
  hasFilters: boolean
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offerer: GetOffererResponseModel | null
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
}

const collectiveFilterStatus = [
  {
    label: 'En instruction',
    value: CollectiveOfferDisplayedStatus.UNDER_REVIEW,
  },
  {
    label: 'Non conforme',
    value: CollectiveOfferDisplayedStatus.REJECTED,
  },
  { label: 'Publiée sur ADAGE', value: CollectiveOfferDisplayedStatus.PUBLISHED },
  {
    label: 'En pause',
    value: CollectiveOfferDisplayedStatus.HIDDEN,
  },
  { label: 'Archivée', value: CollectiveOfferDisplayedStatus.ARCHIVED },
  {
    label: 'Brouillon',
    value: CollectiveOfferDisplayedStatus.DRAFT,
  },
  {
    label: 'Terminée',
    value: CollectiveOfferDisplayedStatus.ENDED,
  },
]

type StatusFormValues = {
  status: CollectiveOfferDisplayedStatus[]
  'search-status': string
}

export const TemplateOffersSearchFilters = ({
  hasFilters,
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  offerer,
  disableAllFilters,
  venues,
}: TemplateOffersSearchFiltersProps): JSX.Element => {
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

  const resetCollectiveFilters = async () => {
    await formik.setFieldValue(
      'status',
      DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.status
    )
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
      <FormikProvider value={formik}>
        <SelectAutocomplete
          multi
          name="status"
          label="Statut"
          options={collectiveFilterStatus}
          isOptional
          disabled={disableAllFilters}
        />
      </FormikProvider>
    </OffersTableSearch>
  )
}
