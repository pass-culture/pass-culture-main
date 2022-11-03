import React from 'react'

import { StockFormInfo } from 'components/StockFormInfo'

import { StockFormActions } from './SockFormActions'
import { IStockFormRowAction } from './SockFormActions/types'
import styles from './StockFormRow.module.scss'

export interface IStockFormRowProps {
  Form: React.ReactNode
  actions?: IStockFormRowAction[]
  actionDisabled: boolean
  showStockInfo?: boolean
}

const StockFormRow = ({
  Form,
  actions,
  actionDisabled,
  showStockInfo = false,
}: IStockFormRowProps): JSX.Element => {
  return (
    <div className={styles['stock-form-row']}>
      <div className={styles['stock-form']}>{Form}</div>

      {showStockInfo && <StockFormInfo className={styles['stock-form-info']} />}

      {actions && actions.length > 0 && (
        <div className={styles['stock-actions']}>
          <StockFormActions actions={actions} disabled={actionDisabled} />
        </div>
      )}
    </div>
  )
}

export default StockFormRow
