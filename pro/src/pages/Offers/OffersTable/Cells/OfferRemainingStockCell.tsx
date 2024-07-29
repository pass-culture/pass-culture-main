import classNames from 'classnames'

import {
  CollectiveOffersStockResponseModel,
  ListOffersStockResponseModel,
} from 'apiClient/v1'

import styles from './Cells.module.scss'

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
}

export const OfferRemainingStockCell = ({
  stocks,
}: OfferRemainingStockCellProps) => {
  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['stock-column']
      )}
    >
      {computeRemainingStockValue(stocks)}
    </td>
  )
}
