import React, { Dispatch, SetStateAction, useCallback } from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import { getToday } from 'utils/date'

type selectableOptionsType = [
  {
    id: string
    displayName: string
  }
]

type filtersType = {
  businessUnit: string
  periodStart: Date
  periodEnd: Date
}

interface IReimbursementsSectionHeaderProps {
  areFiltersDefault: boolean
  children: React.ReactNode | React.ReactNode[]
  defaultSelectDisplayName: string
  defaultSelectId: string
  filters: filtersType
  hasNoInvoicesYet: boolean
  headerTitle: string
  initialFilters: filtersType
  loadInvoices: (shouldReset: boolean) => void
  selectLabel: string
  selectName: string
  selectableOptions: selectableOptionsType
  setAreFiltersDefault: Dispatch<SetStateAction<boolean>>
  setFilters: Dispatch<SetStateAction<filtersType>>
}

const InvoicesFilters = ({
  areFiltersDefault,
  children,
  defaultSelectDisplayName,
  defaultSelectId,
  filters,
  hasNoInvoicesYet,
  headerTitle,
  initialFilters,
  loadInvoices,
  selectLabel,
  selectName,
  selectableOptions,
  setAreFiltersDefault,
  setFilters,
}: IReimbursementsSectionHeaderProps): JSX.Element => {
  const {
    businessUnit: selectedBusinessUnit,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
    loadInvoices(true)
  }

  const setBusinessUnitFilter = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      const businessUnitId = event.target.value
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        businessUnit: businessUnitId,
      }))
      setAreFiltersDefault(false)
    },
    [setAreFiltersDefault, setFilters]
  )

  const setStartDateFilter = useCallback(
    (startDate: Date) => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodStart: startDate,
      }))
      setAreFiltersDefault(false)
    },
    [setAreFiltersDefault, setFilters]
  )

  const setEndDateFilter = useCallback(
    (endDate: Date) => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodEnd: endDate,
      }))
      setAreFiltersDefault(false)
    },
    [setAreFiltersDefault, setFilters]
  )

  return (
    <>
      <div className="header">
        <h2 className="header-title">{headerTitle}</h2>
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
            displayName: defaultSelectDisplayName,
            id: defaultSelectId,
          }}
          handleSelection={setBusinessUnitFilter}
          isDisabled={hasNoInvoicesYet}
          label={selectLabel}
          name={selectName}
          options={selectableOptions}
          selectedValue={selectedBusinessUnit}
        />
        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={hasNoInvoicesYet}
          label="Période"
          maxDateEnding={getToday()}
          periodBeginningDate={selectedPeriodStart}
          periodEndingDate={selectedPeriodEnd}
          todayDate={getToday()}
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
