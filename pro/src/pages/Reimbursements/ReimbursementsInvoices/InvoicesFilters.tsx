import React, { Dispatch, SetStateAction } from 'react'

import FormLayout from 'components/FormLayout/FormLayout'
import { SelectOption } from 'custom_types/form'
import useActiveFeature from 'hooks/useActiveFeature'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import PeriodSelector from 'ui-kit/form/PeriodSelector/PeriodSelector'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import { getToday } from 'utils/date'

import styles from './InvoicesFilters.module.scss'
import { FiltersType } from './types'

interface ReimbursementsSectionHeaderProps {
  areFiltersDefault: boolean
  filters: FiltersType
  disable: boolean
  initialFilters: FiltersType
  loadInvoices: (shouldReset: boolean) => void
  selectableOptions: SelectOption[]
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<FiltersType>>
}

const InvoicesFilters = ({
  areFiltersDefault,
  filters,
  disable,
  initialFilters,
  loadInvoices,
  selectableOptions,
  setAreFiltersDefault,
  setFilters,
}: ReimbursementsSectionHeaderProps): JSX.Element => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )

  const {
    reimbursementPoint: selectedReimbursementPoint,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
    loadInvoices(true)
  }

  const setReimbursementPointFilter = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const reimbursementPointId = event.target.value
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      reimbursementPoint: reimbursementPointId,
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
      <div className={styles['header']}>
        <h2 className={styles['header-title']}>
          Affichage des justificatifs de remboursement
        </h2>
        <Button
          className={styles['reset-filters']}
          disabled={areFiltersDefault}
          onClick={resetFilters}
          variant={ButtonVariant.TERNARYPINK}
        >
          Réinitialiser les filtres
        </Button>
      </div>

      <FormLayout.Row inline>
        <FieldLayout
          label={
            isNewBankDetailsJourneyEnabled
              ? 'Compte bancaire'
              : 'Point de remboursement'
          }
          name="reimbursementPoint"
        >
          <SelectInput
            defaultOption={{
              label: isNewBankDetailsJourneyEnabled
                ? 'Tous les comptes bancaires'
                : 'Tous les points de remboursement',
              value: 'all',
            }}
            onChange={setReimbursementPointFilter}
            disabled={disable}
            name="reimbursementPoint"
            options={selectableOptions}
            value={selectedReimbursementPoint}
          />
        </FieldLayout>

        <fieldset>
          <legend>Période</legend>
          <PeriodSelector
            onBeginningDateChange={setStartDateFilter}
            onEndingDateChange={setEndDateFilter}
            isDisabled={disable}
            maxDateEnding={getToday()}
            periodBeginningDate={selectedPeriodStart}
            periodEndingDate={selectedPeriodEnd}
          />
        </fieldset>
      </FormLayout.Row>

      <div className={styles['button-group']}>
        <div className={styles['button-group-separator']} />
      </div>
    </>
  )
}

export default InvoicesFilters
