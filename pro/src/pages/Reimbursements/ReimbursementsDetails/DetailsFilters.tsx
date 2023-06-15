import React, { Dispatch, SetStateAction, useState } from 'react'

import PeriodSelector from 'ui-kit/form_raw/PeriodSelector/PeriodSelector'
import Select from 'ui-kit/form_raw/Select'
import { getToday } from 'utils/date'

type SelectableOptionsType = {
  id: string
  displayName: string
}

type FiltersType = {
  venue: string
  periodStart: Date
  periodEnd: Date
}

interface ReimbursementsSectionHeaderProps {
  children: React.ReactNode | React.ReactNode[]
  defaultSelectDisplayName: string
  defaultSelectId: string
  filters: FiltersType
  headerTitle: string
  initialFilters: FiltersType
  selectLabel: string
  selectName: string
  setFilters: Dispatch<SetStateAction<FiltersType>>
  selectableOptions: SelectableOptionsType[]
}

const DetailsFilters = ({
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
}: ReimbursementsSectionHeaderProps): JSX.Element => {
  const {
    venue: selectedVenue,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  const [areFiltersDefault, setAreFiltersDefault] = useState(true)

  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
  }

  const setVenueFilter = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const venueId = event.target.value
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      venue: venueId,
    }))
    setAreFiltersDefault(false)
  }

  const setStartDateFilter = (startDate: Date) => {
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      periodStart: startDate,
    }))
    setAreFiltersDefault(false)
  }

  const setEndDateFilter = (endDate: Date) => {
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      periodEnd: endDate,
    }))
    setAreFiltersDefault(false)
  }

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
          handleSelection={setVenueFilter}
          label={selectLabel}
          name={selectName}
          options={selectableOptions}
          selectedValue={selectedVenue}
        />

        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={false}
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

export default DetailsFilters
