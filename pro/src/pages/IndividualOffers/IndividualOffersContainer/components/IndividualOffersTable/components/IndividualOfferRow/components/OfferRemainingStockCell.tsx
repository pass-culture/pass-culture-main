import classNames from 'classnames'

import {
  CollectiveOffersStockResponseModel,
  ListOffersStockResponseModel,
} from 'apiClient/v1'
import styles from 'styles/components/Cells.module.scss'

const computeRemainingStockValue = (
  stocks: (CollectiveOffersStockResponseModel | ListOffersStockResponseModel)[]
) => {
  let totalRemainingStock = 0

  for (const stock of stocks) {
    if (stock.remainingQuantity === 'unlimited') {
      return 'Illimité'
    }
    totalRemainingStock += Number(stock.remainingQuantity)
  }
  return new Intl.NumberFormat('fr-FR').format(totalRemainingStock)
}

interface OfferRemainingStockCellProps {
  stocks: (CollectiveOffersStockResponseModel | ListOffersStockResponseModel)[]
  displayLabel?: boolean
  className?: string
}

export const OfferRemainingStockCell = ({
  stocks,
  displayLabel,
  className,
}: OfferRemainingStockCellProps) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['stock-column'],
        className
      )}
    >
      {displayLabel &&
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          Stocks :
        </span>}
      {computeRemainingStockValue(stocks)}
    </td>
  )
}
