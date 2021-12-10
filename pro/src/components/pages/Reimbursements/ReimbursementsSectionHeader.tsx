import isEqual from 'lodash.isequal'
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
  spot: string
  periodStart: Date
  periodEnd: Date
}

interface IReimbursementsSectionHeaderProps {
  children: React.ReactNode | React.ReactNode[]
  defaultSelectDisplayName: string
  defaultSelectId: string
  filters: filtersType
  headerTitle: string
  initialFilters: filtersType
  selectLabel: string
  selectName: string
  setFilters: Dispatch<SetStateAction<filtersType>>
  selectableOptions: selectableOptionsType
}

const ReimbursementsSectionHeader = ({
  children,
  defaultSelectDisplayName,
  defaultSelectId,
  headerTitle,
  initialFilters,
  selectLabel,
  selectName,
  selectableOptions,
  filters,
  setFilters,
}: IReimbursementsSectionHeaderProps): JSX.Element => {
  const {
    spot: selectedSpot,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  function resetFilters() {
    setFilters(initialFilters)
  }

  const setSpotFilter = useCallback(
    event => {
      const spotId = event.target.value
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        spot: spotId,
      }))
    },
    [setFilters]
  )

  const setStartDateFilter = useCallback(
    startDate => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodStart: startDate,
      }))
    },
    [setFilters]
  )

  const setEndDateFilter = useCallback(
    endDate => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodEnd: endDate,
      }))
    },
    [setFilters]
  )

  return (
    <>
      <div className="header">
        <h2 className="header-title">{headerTitle}</h2>
        <button
          className="tertiary-button reset-filters"
          disabled={isEqual(filters, initialFilters)}
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
          handleSelection={setSpotFilter}
          label={selectLabel}
          name={selectName}
          options={selectableOptions}
          selectedValue={selectedSpot}
        />
        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={false}
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

export default ReimbursementsSectionHeader
