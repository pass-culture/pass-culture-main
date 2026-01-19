import type { Dispatch, SetStateAction } from 'react'
import { useSearchParams } from 'react-router'

import type { SelectOption } from '@/commons/custom_types/form'
import { getToday } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './InvoicesFilters.module.scss'
import type { FiltersType } from './types'

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
            <Select
              label="Compte bancaire"
              defaultOption={{
                label: 'Tous les comptes bancaires',
                value: 'all',
              }}
              onChange={setReimbursementPointFilter}
              name="reimbursementPoint"
              options={selectableOptions}
              value={filters.reimbursementPoint}
            />
          )}

          <PeriodSelector
            legend="Période"
            onBeginningDateChange={setStartDateFilter}
            onEndingDateChange={setEndDateFilter}
            maxDateEnding={getToday()}
            periodBeginningDate={filters.periodStart}
            periodEndingDate={filters.periodEnd}
          />
        </FormLayout.Row>
        <div className={styles['reset-filters']}>
          <Button
            disabled={areFiltersDefault}
            onClick={onReset}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullRefreshIcon}
            label={pluralizeFr(
              selectableOptions.length,
              'Réinitialiser le filtre',
              'Réinitialiser les filtres'
            )}
          />
        </div>
      </div>

      <div className={styles['button-group']}>
        <div className={styles['button-group-separator']} />
        <div className={styles['button-group-button']}>
          <Button
            disabled={!filters.periodStart || !filters.periodEnd}
            onClick={onSearch}
            label="Lancer la recherche"
          />
        </div>
      </div>
    </>
  )
}
