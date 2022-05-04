import React, {
  Dispatch,
  MouseEventHandler,
  SetStateAction,
  useCallback,
  useState,
} from 'react'

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
  venue: string
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
}: IReimbursementsSectionHeaderProps): JSX.Element => {
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

  const setVenueFilter = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => {
      const venueId = event.target.value
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        venue: venueId,
      }))
      setAreFiltersDefault(false)
    },
    [setFilters]
  )

  const setStartDateFilter = useCallback(
    (startDate: Date) => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodStart: startDate,
      }))
      setAreFiltersDefault(false)
    },
    [setFilters]
  )

  const setEndDateFilter = useCallback(
    (endDate: Date) => {
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        periodEnd: endDate,
      }))
      setAreFiltersDefault(false)
    },
    [setFilters]
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

export default DetailsFilters
