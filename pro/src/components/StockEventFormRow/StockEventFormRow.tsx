import React from 'react'

import { StockFormActions } from '../StockFormActions'
import { IStockFormRowAction } from '../StockFormActions/types'

import { StockEventFormInfo } from './StockEventFormInfo'
import styles from './StockEventFormRow.module.scss'

export interface IStockEventFormRowProps {
  Form: React.ReactNode
  stockIndex: number
  actions?: IStockFormRowAction[]
  actionDisabled: boolean
  showStockInfo: boolean
}

const StockEventFormRow = ({
  Form,
  actions,
  stockIndex,
  actionDisabled,
  showStockInfo,
}: IStockEventFormRowProps): JSX.Element => {
  return (
    <div className={styles['stock-form-row']}>
      <div className={styles['stock-form']}>{Form}</div>

      {showStockInfo && (
        <StockEventFormInfo
          className={styles['stock-form-info']}
          index={stockIndex}
        />
      )}

      {actions && actions.length > 0 && (
        <div className={styles['stock-actions']}>
          <StockFormActions actions={actions} disabled={actionDisabled} />
        </div>
      )}
    </div>
  )
}

export default StockEventFormRow
