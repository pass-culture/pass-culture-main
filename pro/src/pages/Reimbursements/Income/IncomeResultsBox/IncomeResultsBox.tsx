import type {
  AggregatedRevenueModel,
  CollectiveRevenue,
  IndividualRevenue,
  TotalRevenue,
} from '@/apiClient//v1'
import fullHelpIcon from '@/icons/full-help.svg'
import { BoxRounded } from '@/ui-kit/BoxRounded/BoxRounded'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'
import { Tooltip } from '@/ui-kit/Tooltip/Tooltip'

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
          <div className={styles['income-results-block-tooltip']}>
            <Tooltip content={help}>
              <button
                type="button"
                className={styles['income-results-block-tooltip-button']}
              >
                <SvgIcon
                  src={fullHelpIcon}
                  alt="À propos"
                  className={styles['income-results-block-tooltip-button-icon']}
                />
              </button>
            </Tooltip>
          </div>
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
    <BoxRounded>
      <div className={styles['income-results-box']}>
        <IncomeResultsSubBox
          title={totalLabel}
          number={total}
          help={totalHelp}
        />
        {shouldDisplayIncomeDetails && (
          <>
            <IncomeResultsSubBox
              title="Part individuelle"
              number={income.individual}
            />
            <IncomeResultsSubBox
              title="Part collective"
              number={income.collective}
            />
          </>
        )}
      </div>
    </BoxRounded>
  )
}
