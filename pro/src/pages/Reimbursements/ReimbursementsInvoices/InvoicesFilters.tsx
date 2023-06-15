import React, { Dispatch, SetStateAction } from 'react'

import PeriodSelector from 'ui-kit/form_raw/PeriodSelector/PeriodSelector'
import Select from 'ui-kit/form_raw/Select'
import { getToday } from 'utils/date'

import { TFiltersType } from './types'

interface ReimbursementsSectionHeaderProps {
  areFiltersDefault: boolean
  children: React.ReactNode | React.ReactNode[]
  filters: TFiltersType
  disable: boolean
  initialFilters: TFiltersType
  loadInvoices: (shouldReset: boolean) => void
  selectableOptions: SelectOptionsRFF
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

      <div className="filters">
        <Select
          defaultOption={{
            displayName: 'Tous les points de remboursement',
            id: 'all',
          }}
          handleSelection={setReimbursementPointFilter}
          isDisabled={disable}
          label="Point de remboursement"
          name="reimbursementPoint"
          options={selectableOptions}
          selectedValue={selectedReimbursementPoint}
        />

        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={disable}
          label="Période"
          maxDateEnding={getToday()}
          periodBeginningDate={selectedPeriodStart}
          periodEndingDate={selectedPeriodEnd}
        />
      </div>

      <div className="button-group">
        <span className="button-group-separator" />
        <div className="button-group-buttons">{children}</div>
      </div>
    </>
  )
}

export default InvoicesFilters
