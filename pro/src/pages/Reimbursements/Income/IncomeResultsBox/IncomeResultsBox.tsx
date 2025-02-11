import type {
  AggregatedRevenueModel,
  TotalRevenue,
  CollectiveRevenue,
  IndividualRevenue,
} from 'apiClient/v1'
import fullHelpIcon from 'icons/full-help.svg'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { isCollectiveAndIndividualRevenue, isCollectiveRevenue } from '../utils'

import styles from './IncomeResultsBox.module.scss'

type IncomeSubBoxProps = {
  title: string
  number: number
  help?: string
}

const IncomeResultsSubBox = ({ title, number, help }: IncomeSubBoxProps) => {
  const numberStr = number.toLocaleString('fr-FR', {
    style: 'currency',
    currency: 'EUR',
  })

  return (
    <div className={styles['income-results-block']}>
      <div className={styles['income-results-block-title']}>
        {title}
        {help && (
          <Button
            className={styles['income-results-block-tooltip']}
            icon={fullHelpIcon}
            iconAlt="À propos"
            type="button"
            tooltipContent={<>{help}</>}
            variant={ButtonVariant.SECONDARY}
          />
        )}
      </div>
      <div className={styles['income-results-block-number']}>{numberStr}</div>
    </div>
  )
}

type IncomeResultsBoxProps = {
  type: keyof AggregatedRevenueModel
  income: TotalRevenue | CollectiveRevenue | IndividualRevenue
}

export const IncomeResultsBox = ({ type, income }: IncomeResultsBoxProps) => {
  const totalLabel =
    type === 'revenue'
      ? 'Chiffre d’affaires total réalisé'
      : 'Chiffre d’affaires total prévisionnel'
  const totalHelp =
    type === 'revenue'
      ? 'Montant des réservations validées et remboursées.'
      : 'Montant des réservations en cours, validées et remboursées.'
  const shouldDisplayIncomeDetails = isCollectiveAndIndividualRevenue(income)
  const total = isCollectiveAndIndividualRevenue(income)
    ? income.total
    : isCollectiveRevenue(income)
      ? income.collective
      : income.individual

  return (
    <BoxRounded className={styles['income-results-box']}>
      <IncomeResultsSubBox title={totalLabel} number={total} help={totalHelp} />
      {shouldDisplayIncomeDetails && (
        <div className={styles['income-results-box-subbox']}>
          <IncomeResultsSubBox
            title="Part individuelle"
            number={income.individual}
          />
          <IncomeResultsSubBox
            title="Part collective"
            number={income.collective}
          />
        </div>
      )}
    </BoxRounded>
  )
}
