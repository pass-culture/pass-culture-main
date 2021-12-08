import isEqual from 'lodash.isequal'
import React, { useCallback, useState } from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import Select from 'components/layout/inputs/Select'
import { getToday } from 'utils/date'

type venuesOptionsType = [
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
  filters: filtersType
  headerTitle: string
  initialFilters: filtersType
  setFilters: any
  venuesOptions: venuesOptionsType
}

const ReimbursementsSectionHeader = ({
  children,
  headerTitle,
  initialFilters,
  venuesOptions,
  filters,
  setFilters,
}: IReimbursementsSectionHeaderProps): JSX.Element => {
  const ALL_VENUES_OPTION_ID = 'allVenues'

  const {
    venue: selectedVenue,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  function resetFilters() {
    setFilters(initialFilters)
  }

  const setVenueFilter = useCallback(
    event => {
      const venueId = event.target.value
      setFilters((prevFilters: filtersType) => ({
        ...prevFilters,
        venue: venueId,
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
            displayName: 'Tous les lieux',
            id: ALL_VENUES_OPTION_ID,
          }}
          handleSelection={setVenueFilter}
          label="Lieu"
          name="lieu"
          options={venuesOptions}
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

export default ReimbursementsSectionHeader
