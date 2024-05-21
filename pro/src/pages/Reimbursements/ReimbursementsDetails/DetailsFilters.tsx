import React, { Dispatch, SetStateAction, useState } from 'react'

import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { SelectOption } from 'custom_types/form'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { PeriodSelector } from 'ui-kit/form/PeriodSelector/PeriodSelector'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'
import { getToday } from 'utils/date'

import styles from './DetailsFilters.module.scss'

type FiltersType = {
  bankAccount: string
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

export const DetailsFilters = ({
  children,
  defaultSelectId,
  initialFilters,
  selectableOptions,
  filters,
  setFilters,
}: ReimbursementsSectionHeaderProps): JSX.Element => {
  const {
    bankAccount: selectedBankAccount,
    periodStart: selectedPeriodStart,
    periodEnd: selectedPeriodEnd,
  } = filters

  const [areFiltersDefault, setAreFiltersDefault] = useState(true)

  function resetFilters() {
    setAreFiltersDefault(true)
    setFilters(initialFilters)
  }

  const setBankAccountFilter = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const bankAccountId = event.target.value
    setFilters((prevFilters: FiltersType) => ({
      ...prevFilters,
      bankAccount: bankAccountId,
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
      <Callout variant={CalloutVariant.INFO}>
        Nouveau ! Les détails de remboursements seront bientôt téléchargeables
        depuis l’onglet justificatif.
      </Callout>
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

      <FormLayout.Row inline>
        <FieldLayout label="Compte bancaire" name="compte-bancaire" isOptional>
          <SelectInput
            defaultOption={{
              label: 'Tous les comptes bancaires',
              value: defaultSelectId,
            }}
            onChange={setBankAccountFilter}
            name="compte-bancaire"
            options={selectableOptions}
            value={selectedBankAccount}
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
