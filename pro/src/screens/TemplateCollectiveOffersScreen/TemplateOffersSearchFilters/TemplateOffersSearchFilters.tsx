import { FormikProvider, useFormik } from 'formik'
import { Dispatch, FormEvent, SetStateAction, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

import {
  CollectiveOfferDisplayedStatus,
  EacFormat,
  GetOffererResponseModel,
} from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  ALL_FORMATS_OPTION,
  ALL_VENUES_OPTION,
  DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { hasCollectiveSearchFilters } from 'core/Offers/utils/hasSearchFilters'
import { SelectOption } from 'custom_types/form'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import fullRefreshIcon from 'icons/full-refresh.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { SelectAutocomplete } from 'ui-kit/form/SelectAutoComplete/SelectAutocomplete'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './TemplateOffersSearchFilters.module.scss'

interface TemplateOffersSearchFiltersProps {
  applyFilters: (filters: CollectiveSearchFiltersParams) => void
  offerer: GetOffererResponseModel | null
  removeOfferer: () => void
  selectedFilters: CollectiveSearchFiltersParams
  setSelectedFilters: Dispatch<SetStateAction<CollectiveSearchFiltersParams>>
  disableAllFilters: boolean
  resetFilters: () => void
  venues: SelectOption[]
  categories?: SelectOption[]
  isRestrictedAsAdmin?: boolean
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

export const TemplateOffersSearchFilters = ({
  applyFilters,
  selectedFilters,
  setSelectedFilters,
  resetFilters,
  offerer,
  removeOfferer,
  disableAllFilters,
  venues,
  isRestrictedAsAdmin = false,
}: TemplateOffersSearchFiltersProps): JSX.Element => {
  const { t } = useTranslation('common')
  const isNewInterfaceActive = useIsNewInterfaceActive()
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
    applyFilters({
      ...selectedFilters,
      offererId: offerer?.id.toString() ?? '',
    })
  }

  const resetCollectiveFilters = async () => {
    await formik.setFieldValue(
      'status',
      DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS.status
    )
    resetFilters()
  }

  const searchByOfferNameLabel = 'Nom de l’offre'
  const searchByOfferNamePlaceholder = 'Rechercher par nom d’offre'

  return (
    <>
      {!isNewInterfaceActive && offerer && (
        <span className="offerer-filter">
          {offerer.name}
          <button
            onClick={removeOfferer}
            type="button"
            data-testid="remove-offerer-filter"
          >
            <SvgIcon
              src={strokeCloseIcon}
              alt="Supprimer le filtre par structure"
              className={styles['offerer-close-icon']}
            />
          </button>
        </span>
      )}
      <form
        onSubmit={requestFilteredOffers}
        className={styles['search-filters-form']}
      >
        <FieldLayout label={searchByOfferNameLabel} name="offre" isOptional>
          <BaseInput
            type="text"
            disabled={disableAllFilters}
            name="offre"
            onChange={storeNameOrIsbnSearchValue}
            placeholder={searchByOfferNamePlaceholder}
            value={selectedFilters.nameOrIsbn}
          />
        </FieldLayout>
        <FormLayout.Row inline>
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

          <fieldset>
            <legend>Période de l’évènement</legend>

            <PeriodSelector
              onBeginningDateChange={onBeginningDateChange}
              onEndingDateChange={onEndingDateChange}
              isDisabled={disableAllFilters}
              periodBeginningDate={selectedFilters.periodBeginningDate}
              periodEndingDate={selectedFilters.periodEndingDate}
            />
          </fieldset>
        </FormLayout.Row>

        <FormikProvider value={formik}>
          <SelectAutocomplete
            multi
            name="status"
            label={
              <span className={styles['status-filter-label']}>Statut</span>
            }
            options={collectiveFilterStatus}
            placeholder="Statuts"
            isOptional
            className={styles['status-filter']}
            disabled={disableAllFilters || isRestrictedAsAdmin}
          />
        </FormikProvider>

        <div className={styles['reset-filters']}>
          <Button
            icon={fullRefreshIcon}
            disabled={
              !hasCollectiveSearchFilters(
                selectedFilters,
                DEFAULT_COLLECTIVE_TEMPLATE_SEARCH_FILTERS
              )
            }
            onClick={resetCollectiveFilters}
            variant={ButtonVariant.TERNARY}
          >
            Réinitialiser les filtres
          </Button>
        </div>
        <div className={styles['search-separator']}>
          <div className={styles['separator']} />
          <Button type="submit" disabled={disableAllFilters}>
            {t('search')}
          </Button>
          <div className={styles['separator']} />
        </div>
      </form>
    </>
  )
}
