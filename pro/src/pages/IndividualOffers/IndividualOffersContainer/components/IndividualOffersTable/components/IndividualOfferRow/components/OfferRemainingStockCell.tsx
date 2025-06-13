import classNames from 'classnames'

import {
  CollectiveOffersStockResponseModel,
  ListOffersStockResponseModel,
} from 'apiClient/v1'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
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
  rowId: string
  stocks: (CollectiveOffersStockResponseModel | ListOffersStockResponseModel)[]
  displayLabel?: boolean
  className?: string
}

export const OfferRemainingStockCell = ({
  rowId,
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
      headers={`${rowId} ${getCellsDefinition().STOCKS.id}`}
    >
      {displayLabel && (
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          {`${getCellsDefinition().STOCKS.title} :`}
        </span>
      )}
      {computeRemainingStockValue(stocks)}
    </td>
  )
}
