import { format, startOfDay, subDays } from 'date-fns'
import { useState } from 'react'
import { useSearchParams } from 'react-router'

import type { BankAccountResponseModel } from '@/apiClient/v1'
import { FORMAT_ISO_DATE_ONLY, getToday } from '@/commons/utils/date'
import { sortByLabel } from '@/commons/utils/strings'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { TextInput } from '@/design-system/TextInput/TextInput'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './SettlementsFilters.module.scss'

const DEFAULT_SETTLEMENTS_PERIOD = 30
const ALL_ACCOUNTS = 'ALL_ACCOUNTS'

type SettlementsFiltersProps = {
  bankAccounts: BankAccountResponseModel[]
  onReset: () => void
}

function getDefaultBeginigDate() {
  return format(
    startOfDay(subDays(getToday(), DEFAULT_SETTLEMENTS_PERIOD)),
    FORMAT_ISO_DATE_ONLY
  )
}

function getDefaultEndingDate() {
  return format(startOfDay(getToday()), FORMAT_ISO_DATE_ONLY)
}

function computeFilterState(
  searchParams: URLSearchParams,
  nameSearch: string,
  bankAccountId: string,
  periodBeginningDate: string,
  periodEndingDate: string
) {
  const urlNameSearch = searchParams.get('nameSearch') ?? ''
  const urlBankAccountId = searchParams.get('bankAccountId') ?? ALL_ACCOUNTS
  const urlPeriodBeginningDate = searchParams.get('periodBeginningDate')
  const urlPeriodEndingDate = searchParams.get('periodEndingDate')

  const hasCustomFilters =
    urlNameSearch !== '' ||
    urlBankAccountId !== ALL_ACCOUNTS ||
    urlPeriodBeginningDate !== getDefaultBeginigDate() ||
    urlPeriodEndingDate !== getDefaultEndingDate()

  const errors = {
    beginningDate: !periodBeginningDate
      ? 'La date de début est obligatoire'
      : '',
    endingDate: !periodEndingDate ? 'La date de fin est obligatoire' : '',
  }

  const canRelaunchSearch =
    !errors.beginningDate &&
    !errors.endingDate &&
    (nameSearch !== urlNameSearch ||
      bankAccountId !== urlBankAccountId ||
      periodBeginningDate !== urlPeriodBeginningDate ||
      periodEndingDate !== urlPeriodEndingDate)

  return { hasCustomFilters, canRelaunchSearch, errors }
}

export const SettlementsFilters = ({
  bankAccounts,
  onReset,
}: Readonly<SettlementsFiltersProps>): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()

  const [nameSearch, setNameSearch] = useState(
    searchParams.get('nameSearch') ?? ''
  )

  const [periodBeginningDate, setPeriodBeginningDate] = useState(
    searchParams.get('periodBeginningDate') ?? getDefaultBeginigDate()
  )
  const [periodEndingDate, setPeriodEndingDate] = useState(
    searchParams.get('periodEndingDate') ?? getDefaultEndingDate()
  )

  const [bankAccountId, setBankAccountId] = useState<string>(
    searchParams.get('bankAccountId') ?? ALL_ACCOUNTS
  )

  const bankAccountOptions = sortByLabel(
    bankAccounts.map((item) => ({
      value: String(item.id),
      label: item.label,
    }))
  )

  const { hasCustomFilters, canRelaunchSearch, errors } = computeFilterState(
    searchParams,
    nameSearch,
    bankAccountId,
    periodBeginningDate,
    periodEndingDate
  )

  function onSearch() {
    const newFilters = {
      periodBeginningDate,
      periodEndingDate,
      ...(bankAccountId !== ALL_ACCOUNTS && { bankAccountId }),
      ...(nameSearch && { nameSearch }),
    }
    setSearchParams(newFilters)
  }

  return (
    <>
      <div className={styles['filters']}>
        <FormLayout.Row inline className={styles['selectors']}>
          <TextInput
            name="nameSearch"
            label="N° de virement"
            value={nameSearch}
            onChange={({ target: { value } }) => setNameSearch(value)}
          />

          <Select
            label="Compte bancaire"
            name="bankAccount"
            defaultOption={{
              label: 'Tous les comptes bancaires',
              value: ALL_ACCOUNTS,
            }}
            options={bankAccountOptions}
            value={bankAccountId}
            onChange={({ target: { value } }) => setBankAccountId(value)}
          />

          <PeriodSelector
            legend="Période d'émission"
            onBeginningDateChange={setPeriodBeginningDate}
            onEndingDateChange={setPeriodEndingDate}
            maxDateEnding={getToday()}
            periodBeginningDate={periodBeginningDate}
            periodEndingDate={periodEndingDate}
            errors={errors}
          />
        </FormLayout.Row>
        {hasCustomFilters && (
          <div className={styles['reset-filters']}>
            <Button
              onClick={onReset}
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              icon={fullRefreshIcon}
              label="Réinitialiser les filtres"
            />
          </div>
        )}
      </div>

      <div className={styles['button-group']}>
        <div className={styles['button-group-separator']} />
        <div className={styles['button-group-button']}>
          <Button
            disabled={!canRelaunchSearch}
            onClick={onSearch}
            label="Lancer la recherche"
          />
        </div>
      </div>
    </>
  )
}
