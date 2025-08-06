import { Dispatch, SetStateAction } from 'react'
import { useSearchParams } from 'react-router'

import { SelectOption } from '@/commons/custom_types/form'
import { getToday } from '@/commons/utils/date'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './InvoicesFilters.module.scss'
import { FiltersType } from './types'

interface InvoicesFiltersProps {
  areFiltersDefault: boolean
  filters: FiltersType
  selectableOptions: SelectOption[]
  setFilters: Dispatch<SetStateAction<FiltersType>>
  onReset: () => void
  onSearch: () => void
}

export const InvoicesFilters = ({
  areFiltersDefault,
  filters,
  selectableOptions,
  setFilters,
  onReset,
  onSearch,
}: InvoicesFiltersProps): JSX.Element => {
  const [searchParams] = useSearchParams()

  const setReimbursementPointFilter = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const reimbursementPoint = event.target.value
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      reimbursementPoint,
    }))
    searchParams.set('reimbursementPoint', filters.reimbursementPoint)
  }

  const setStartDateFilter = (startDate: string) => {
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      periodStart: startDate,
    }))
    searchParams.set('periodStart', filters.periodStart)
  }

  const setEndDateFilter = (endDate: string) => {
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      periodEnd: endDate,
    }))
    searchParams.set('periodEnd', filters.periodEnd)
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
                value={filters.reimbursementPoint}
              />
            </FieldLayout>
          )}

          <fieldset>
            <legend>Période</legend>
            <PeriodSelector
              onBeginningDateChange={setStartDateFilter}
              onEndingDateChange={setEndDateFilter}
              maxDateEnding={getToday()}
              periodBeginningDate={filters.periodStart}
              periodEndingDate={filters.periodEnd}
            />
          </fieldset>
        </FormLayout.Row>
        <Button
          className={styles['reset-filters']}
          disabled={areFiltersDefault}
          onClick={onReset}
          variant={ButtonVariant.TERNARY}
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
            onClick={onSearch}
          >
            Lancer la recherche
          </Button>
        </div>
      </div>
    </>
  )
}
