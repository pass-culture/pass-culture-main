import React, { Dispatch, SetStateAction } from 'react'

import FormLayout from 'components/FormLayout/FormLayout'
import { SelectOption } from 'custom_types/form'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import PeriodSelector from 'ui-kit/form_raw/PeriodSelector/PeriodSelector'
import { getToday } from 'utils/date'

import { TFiltersType } from './types'

interface ReimbursementsSectionHeaderProps {
  areFiltersDefault: boolean
  children: React.ReactNode | React.ReactNode[]
  filters: TFiltersType
  disable: boolean
  initialFilters: TFiltersType
  loadInvoices: (shouldReset: boolean) => void
  selectableOptions: SelectOption[]
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<TFiltersType>>
}

const InvoicesFilters = ({
  areFiltersDefault,
  children,
  filters,
  disable,
  initialFilters,
  loadInvoices,
  selectableOptions,
  setAreFiltersDefault,
  setFilters,
}: ReimbursementsSectionHeaderProps): JSX.Element => {
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
    setFilters((prevFilters: TFiltersType) => ({
      ...prevFilters,
      reimbursementPoint: reimbursementPointId,
    }))
    setAreFiltersDefault(false)
  }

  const setStartDateFilter = (startDate: Date) => {
    setFilters((prevFilters: TFiltersType) => ({
      ...prevFilters,
      periodStart: startDate,
    }))
    setAreFiltersDefault(false)
  }

  const setEndDateFilter = (endDate: Date) => {
    setFilters((prevFilters: TFiltersType) => ({
      ...prevFilters,
      periodEnd: endDate,
    }))
    setAreFiltersDefault(false)
  }

  return (
    <>
      <div className="header">
        <h2 className="header-title">
          Affichage des justificatifs de remboursement
        </h2>
        <button
          className="tertiary-button reset-filters"
          disabled={areFiltersDefault}
          onClick={resetFilters}
          type="button"
        >
          Réinitialiser les filtres
        </button>
      </div>

      <FormLayout.Row inline>
        <FieldLayout label="Point de remboursement" name="reimbursementPoint">
          <SelectInput
            defaultOption={{
              label: 'Tous les points de remboursement',
              value: 'all',
            }}
            onChange={setReimbursementPointFilter}
            disabled={disable}
            name="reimbursementPoint"
            options={selectableOptions}
            value={selectedReimbursementPoint}
          />
        </FieldLayout>

        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={disable}
          label="Période"
          maxDateEnding={getToday()}
          periodBeginningDate={selectedPeriodStart}
          periodEndingDate={selectedPeriodEnd}
        />
      </FormLayout.Row>

      <div className="button-group">
        <span className="button-group-separator" />
        <div className="button-group-buttons">{children}</div>
      </div>
    </>
  )
}

export default InvoicesFilters
