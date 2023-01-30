import cn from 'classnames'
import React from 'react'

import { StockFormActions } from '../StockFormActions'
import { IStockFormRowAction } from '../StockFormActions/types'

import { StockEventFormInfo } from './StockEventFormInfo'
import styles from './StockEventFormRow.module.scss'

export interface IStockEventFormRowProps {
  children?: React.ReactNode
  stockIndex: number
  actions?: IStockFormRowAction[]
  actionDisabled: boolean
  showStockInfo: boolean
}

const StockEventFormRow = ({
  children,
  actions,
  stockIndex,
  actionDisabled,
  showStockInfo,
}: IStockEventFormRowProps): JSX.Element => {
  return (
    <div className={styles['stock-form-row']}>
      <div className={styles['stock-form']}>{children}</div>

      {showStockInfo && (
        <StockEventFormInfo
          className={styles['stock-form-info']}
          stockIndex={stockIndex}
        />
      )}

      {actions && actions.length > 0 && (
        <div
          className={cn(styles['stock-actions'], {
            [styles['stock-first-action']]: stockIndex == 0,
          })}
        >
          <StockFormActions
            actions={actions}
            disabled={actionDisabled}
            stockIndex={stockIndex}
          />
        </div>
      )}
    </div>
  )
}

export default StockEventFormRow
