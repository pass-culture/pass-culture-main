import React from 'react'

import { StockFormInfo } from 'components/StockFormInfo'

import { StockFormActions } from '../StockFormActions'
import { IStockFormRowAction } from '../StockFormActions/types'

import styles from './StockThingFormRow.module.scss'

export interface IStockThingFormRowProps {
  children?: React.ReactNode
  actions?: IStockFormRowAction[]
  actionDisabled: boolean
  showStockInfo?: boolean
}

const StockThingFormRow = ({
  children,
  actions,
  actionDisabled,
  showStockInfo = false,
}: IStockThingFormRowProps): JSX.Element => {
  return (
    <div className={styles['stock-form-row']}>
      <div className={styles['stock-form']}>{children}</div>

      {showStockInfo && <StockFormInfo className={styles['stock-form-info']} />}

      {actions && actions.length > 0 && (
        <div className={styles['stock-actions']}>
          <StockFormActions actions={actions} disabled={actionDisabled} />
        </div>
      )}
    </div>
  )
}

export default StockThingFormRow
