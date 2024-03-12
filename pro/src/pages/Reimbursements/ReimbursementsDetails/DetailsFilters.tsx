import React, { Dispatch, SetStateAction, useState } from 'react'

import FormLayout from 'components/FormLayout/FormLayout'
import { SelectOption } from 'custom_types/form'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import PeriodSelector from 'ui-kit/form/PeriodSelector/PeriodSelector'
import SelectInput from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared'
import { getToday } from 'utils/date'

import styles from './DetailsFilters.module.scss'

type FiltersType = {
  venue: string
  periodStart: string
  periodEnd: string
}

interface ReimbursementsSectionHeaderProps {
  children: React.ReactNode | React.ReactNode[]
  defaultSelectId: string
  filters: FiltersType
  initialFilters: FiltersType
  setFilters: Dispatch<SetStateAction<FiltersType>>
  selectableOptions: SelectOption[]
}

const DetailsFilters = ({
  children,
  defaultSelectId,
  initialFilters,
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
        <h2 className={styles['header-title']}>Affichage des remboursements</h2>
        <Button
          className={styles['reset-filters']}
          disabled={areFiltersDefault}
          onClick={resetFilters}
          variant={ButtonVariant.TERNARYPINK}
        >
          Réinitialiser les filtres
        </Button>
      </div>
      <div className={styles['mandatory']}>
        Tous les champs suivis d’un * sont obligatoires.
      </div>
      <FormLayout.Row inline>
        <FieldLayout label="Lieu" name="lieu">
          <SelectInput
            defaultOption={{
              label: 'Tous les lieux',
              value: defaultSelectId,
            }}
            onChange={setVenueFilter}
            name="lieu"
            options={selectableOptions}
            value={selectedVenue}
          />
        </FieldLayout>

        <fieldset>
          <legend>Période</legend>
          <PeriodSelector
            onBeginningDateChange={setStartDateFilter}
            onEndingDateChange={setEndDateFilter}
            isDisabled={false}
            maxDateEnding={getToday()}
            periodBeginningDate={selectedPeriodStart}
            periodEndingDate={selectedPeriodEnd}
          />
        </fieldset>
      </FormLayout.Row>

      <div className={styles['button-group']}>
        <div className={styles['button-group-separator']} />
        <div className={styles['button-group-buttons']}>{children}</div>
      </div>
    </>
  )
}

export default DetailsFilters
