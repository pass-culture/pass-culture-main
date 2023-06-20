import React, { Dispatch, SetStateAction, useState } from 'react'

import FormLayout from 'components/FormLayout/FormLayout'
import { SelectOption } from 'custom_types/form'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import PeriodSelector from 'ui-kit/form_raw/PeriodSelector/PeriodSelector'
import { getToday } from 'utils/date'

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
  selectableOptions: SelectOption[]
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

      <FormLayout.Row inline>
        <FieldLayout label={selectLabel} name={selectName}>
          <SelectInput
            defaultOption={{
              label: defaultSelectDisplayName,
              value: defaultSelectId,
            }}
            onChange={setVenueFilter}
            name={selectName}
            options={selectableOptions}
            value={selectedVenue}
          />
        </FieldLayout>

        <PeriodSelector
          changePeriodBeginningDateValue={setStartDateFilter}
          changePeriodEndingDateValue={setEndDateFilter}
          isDisabled={false}
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

export default DetailsFilters
