import { useState } from 'react'
import { useSearchParams } from 'react-router'

import { getToday } from '@/commons/utils/date'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullRefreshIcon from '@/icons/full-refresh.svg'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'
import { Select } from '@/ui-kit/form/Select/Select'

import { DEFAULT_INVOICES_FILTERS } from './constants'
import styles from './InvoicesFilters.module.scss'

interface InvoicesFiltersProps {
  onReset: () => void
}

const AMOUNT_FILTER = {
  ALL_AMOUNTS: 'ALL_AMOUNTS',
  POSITIVE_AMOUNT: 'POSITIVE_AMOUNT',
  NEGATIVE_AMOUNT: 'NEGATIVE_AMOUNT',
} as const

type AMOUNT_FILTER = keyof typeof AMOUNT_FILTER

function extractAmountFilters(searchParams: URLSearchParams): AMOUNT_FILTER {
  if (searchParams.get('amountPositiveOnly') === 'true') {
    return AMOUNT_FILTER.POSITIVE_AMOUNT
  }
  if (searchParams.get('amountNegativeOnly') === 'true') {
    return AMOUNT_FILTER.NEGATIVE_AMOUNT
  }
  return AMOUNT_FILTER.ALL_AMOUNTS
}

function amountFilterToQuery(
  amount: AMOUNT_FILTER
): Partial<Record<'amountPositiveOnly' | 'amountNegativeOnly', string>> {
  if (amount === AMOUNT_FILTER.POSITIVE_AMOUNT) {
    return { amountPositiveOnly: 'true' }
  }
  if (amount === AMOUNT_FILTER.NEGATIVE_AMOUNT) {
    return { amountNegativeOnly: 'true' }
  }
  return {}
}

function computeFilterState(
  searchParams: URLSearchParams,
  amount: AMOUNT_FILTER,
  periodBeginningDate: string,
  periodEndingDate: string
) {
  const urlAmounts = extractAmountFilters(searchParams)
  const urlPeriodBeginningDate = searchParams.get('periodBeginningDate')
  const urlPeriodEndingDate = searchParams.get('periodEndingDate')
  const hasCustomFilters =
    urlAmounts !== AMOUNT_FILTER.ALL_AMOUNTS ||
    urlPeriodBeginningDate !== DEFAULT_INVOICES_FILTERS.periodBeginningDate ||
    urlPeriodEndingDate !== DEFAULT_INVOICES_FILTERS.periodEndingDate
  const errors = {
    beginningDate: !periodBeginningDate
      ? 'La date de début est obligatoire'
      : '',
    endingDate: !periodEndingDate ? 'La date de fin est obligatoire' : '',
  }
  const canRelaunchSearch =
    !errors.beginningDate &&
    !errors.endingDate &&
    (amount !== urlAmounts ||
      periodBeginningDate !== urlPeriodBeginningDate ||
      periodEndingDate !== urlPeriodEndingDate)

  return { hasCustomFilters, canRelaunchSearch, errors }
}

export const InvoicesFilters = ({
  onReset,
}: InvoicesFiltersProps): JSX.Element => {
  const [searchParams, setSearchParams] = useSearchParams()

  const [amount, setAmount] = useState<AMOUNT_FILTER>(
    extractAmountFilters(searchParams)
  )
  const [periodBeginningDate, setPeriodBeginningDate] = useState(
    searchParams.get('periodBeginningDate') ??
      DEFAULT_INVOICES_FILTERS.periodBeginningDate
  )
  const [periodEndingDate, setPeriodEndingDate] = useState(
    searchParams.get('periodEndingDate') ??
      DEFAULT_INVOICES_FILTERS.periodEndingDate
  )

  const { hasCustomFilters, canRelaunchSearch, errors } = computeFilterState(
    searchParams,
    amount,
    periodBeginningDate,
    periodEndingDate
  )

  const onSearch = () => {
    setSearchParams({
      periodBeginningDate,
      periodEndingDate,
      ...amountFilterToQuery(amount),
    })
  }

  return (
    <>
      <div className={styles['filters']}>
        <FormLayout.Row inline className={styles['selectors']}>
          <Select
            label="Type de justificatif"
            name="amount"
            defaultOption={{ label: 'Tous les types', value: 'ALL_AMOUNTS' }}
            options={[
              { label: 'Remboursement', value: 'POSITIVE_AMOUNT' },
              { label: 'Trop-perçu', value: 'NEGATIVE_AMOUNT' },
            ]}
            value={amount}
            onChange={({ target: { value } }) =>
              setAmount(value as AMOUNT_FILTER)
            }
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
          <div className="emptyFilter">
            {/* TODO(mdesquilbet, 19/08/2026): Remove this empty slot when the type filter will be added */}
          </div>
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
