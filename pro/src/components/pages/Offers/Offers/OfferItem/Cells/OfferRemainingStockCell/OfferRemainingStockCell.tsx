import React from 'react'

import { Stock } from 'core/Offers/types'

const OfferRemainingStockCell = ({ stocks }: { stocks: Stock[] }) => {
  const computeRemainingStockValue = (stocks: Stock[]) => {
    let totalRemainingStock = 0

    for (const stock of stocks) {
      if (stock.remainingQuantity === 'unlimited') {
        return 'Illimité'
      }
      totalRemainingStock += Number(stock.remainingQuantity)
    }

    return totalRemainingStock
  }

  return <td className="stock-column">{computeRemainingStockValue(stocks)}</td>
}

export default OfferRemainingStockCell
