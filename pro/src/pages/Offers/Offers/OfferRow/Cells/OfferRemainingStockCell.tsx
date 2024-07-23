import React from 'react'

import {
  CollectiveOffersStockResponseModel,
  ListOffersStockResponseModel,
} from 'apiClient/v1'

import styles from '../OfferItem.module.scss'

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
    <td className={styles['stock-column']}>
      {computeRemainingStockValue(stocks)}
    </td>
  )
}
