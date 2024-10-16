import fullHelpIcon from 'icons/full-help.svg'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { IncomeType, IncomeResults } from '../types'

import styles from './IncomeResultsBox.module.scss'

type IncomeSubBoxProps = {
  title: string
  number: number
  help?: string
}

const IncomeResultsSubBox = ({ title, number, help }: IncomeSubBoxProps) => {
  const numberStr = number.toString().replace('.', ',')

  return (
    <div className={styles['income-results-block']}>
      <div className={styles['income-results-block-title']}>
        {title}
        {help && (
          <Button
            className={styles['income-results-block-tooltip']}
            tooltipContentClassName={
              styles['income-results-block-tooltip-content']
            }
            icon={fullHelpIcon}
            iconAlt="À propos"
            type="button"
            hasTooltip
            variant={ButtonVariant.SECONDARY}
          >
            {help}
          </Button>
        )}
      </div>
      <div className={styles['income-results-block-number']}>{numberStr}€</div>
    </div>
  )
}

type IncomeResultsBoxProps = {
  type: IncomeType
  income?: IncomeResults
}

export const IncomeResultsBox = ({ type, income }: IncomeResultsBoxProps) => {
  if (!income) {
    return null
  }

  const totalLabel =
    type === 'aggregatedRevenue'
      ? 'Chiffre d’affaires total réalisé'
      : 'Chiffre d’affaires total prévisionnel'
  const totalHelp =
    type === 'aggregatedRevenue'
      ? 'Montant des réservations validées et remboursées.'
      : 'Montant des réservations en cours, validées et remboursées.'
  const shouldDisplayIncomeDetails = income.individual && income.group

  return (
    <BoxRounded
      className={styles['income-results-box']}
      showButtonModify={false}
    >
      <IncomeResultsSubBox
        title={totalLabel}
        number={income.total}
        help={totalHelp}
      />
      {shouldDisplayIncomeDetails && (
        <div className={styles['income-results-box-subbox']}>
          {income.individual && (
            <IncomeResultsSubBox
              title="Part individuelle"
              number={income.individual}
            />
          )}
          {income.group && (
            <IncomeResultsSubBox
              title="Part collective"
              number={income.group}
            />
          )}
        </div>
      )}
    </BoxRounded>
  )
}
