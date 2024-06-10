import { Dispatch, SetStateAction } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useSWRConfig } from 'swr'

import { FormLayout } from 'components/FormLayout/FormLayout'
import { GET_INVOICES_QUERY_KEY } from 'config/swrQueryKeys'
import { SelectOption } from 'custom_types/form'
import fullRefreshIcon from 'icons/full-refresh.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { getToday } from 'utils/date'

import styles from './InvoicesFilters.module.scss'
import { FiltersType } from './types'

interface ReimbursementsSectionHeaderProps {
  areFiltersDefault: boolean
  filters: FiltersType
  initialFilters: FiltersType
  selectableOptions: SelectOption[]
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<FiltersType>>
  setHasSearchedOnce: Dispatch<SetStateAction<boolean>>
}

export const InvoicesFilters = ({
  areFiltersDefault,
  filters,
  initialFilters,
  selectableOptions,
  setAreFiltersDefault,
  setFilters,
  setHasSearchedOnce,
}: ReimbursementsSectionHeaderProps): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()
  const { mutate } = useSWRConfig()

  const {
    reimbursementPoint: selectedReimbursementPoint,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  function resetFilters() {
    searchParams.set('reimbursementPoint', initialFilters.reimbursementPoint)
    searchParams.set('periodStart', initialFilters.periodStart)
    searchParams.set('periodEnd', initialFilters.periodEnd)
    setSearchParams(searchParams)
    setAreFiltersDefault(true)
    setFilters(initialFilters)
  }

  const setReimbursementPointFilter = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const reimbursementPoint = event.target.value
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      reimbursementPoint,
    }))
    setAreFiltersDefault(false)
  }

  const setStartDateFilter = (startDate: string) => {
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      periodStart: startDate,
    }))
    setAreFiltersDefault(false)
  }

  const setEndDateFilter = (endDate: string) => {
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      periodEnd: endDate,
    }))
    setAreFiltersDefault(false)
  }

  return (
    <>
      <div className={styles['filters']}>
        <FormLayout.Row inline className={styles['selectors']}>
          {selectableOptions.length > 1 && (
            <FieldLayout
              label="Compte bancaire"
              name="reimbursementPoint"
              isOptional
            >
              <SelectInput
                defaultOption={{
                  label: 'Tous les comptes bancaires',
                  value: 'all',
                }}
                onChange={setReimbursementPointFilter}
                name="reimbursementPoint"
                options={selectableOptions}
                value={selectedReimbursementPoint}
              />
            </FieldLayout>
          )}

          <fieldset>
            <legend>Période</legend>
            <PeriodSelector
              onBeginningDateChange={setStartDateFilter}
              onEndingDateChange={setEndDateFilter}
              maxDateEnding={getToday()}
              periodBeginningDate={selectedPeriodStart}
              periodEndingDate={selectedPeriodEnd}
            />
          </fieldset>
        </FormLayout.Row>
        <Button
          className={styles['reset-filters']}
          disabled={areFiltersDefault}
          onClick={resetFilters}
          variant={ButtonVariant.TERNARYPINK}
          icon={fullRefreshIcon}
        >
          {selectableOptions.length === 1
            ? 'Réinitialiser le filtre'
            : 'Réinitialiser les filtres'}
        </Button>
      </div>

      <div className={styles['button-group']}>
        <div className={styles['button-group-separator']} />
        <div className={styles['button-group-button']}>
          <Button
            variant={ButtonVariant.PRIMARY}
            className={styles['button-group-search-button']}
            disabled={!filters.periodStart || !filters.periodEnd}
            onClick={async () => {
              setHasSearchedOnce(true)
              searchParams.set('reimbursementPoint', filters.reimbursementPoint)
              searchParams.set('periodStart', filters.periodStart)
              searchParams.set('periodEnd', filters.periodEnd)
              setSearchParams(searchParams)
              await mutate([GET_INVOICES_QUERY_KEY])
            }}
          >
            Lancer la recherche
          </Button>
        </div>
      </div>
    </>
  )
}
