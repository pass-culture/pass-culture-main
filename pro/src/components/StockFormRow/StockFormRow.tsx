import { useFormikContext } from 'formik'
import React from 'react'

import { StockFormInfo } from 'components/StockFormInfo'
import { IStockThingFormValues } from 'components/StockThingForm'

import { StockFormActions } from './SockFormActions'
import { IStockFormRowAction } from './SockFormActions/types'
import styles from './StockFormRow.module.scss'

export interface IStockFormRowProps {
  Form: React.ReactNode
  actions?: IStockFormRowAction[]
  actionDisabled: boolean
}

const StockFormRow = ({
  Form,
  actions,
  actionDisabled,
}: IStockFormRowProps): JSX.Element => {
  const {
    values: { stockId },
  } = useFormikContext<IStockThingFormValues>()
  return (
    <div className={styles['stock-form-row']}>
      <div className={styles['stock-form']}>{Form}</div>

      {stockId && <StockFormInfo className={styles['stock-form-info']} />}

      {actions && actions.length > 0 && (
        <div className={styles['stock-actions']}>
          <StockFormActions actions={actions} disabled={actionDisabled} />
        </div>
      )}
    </div>
  )
}

export default StockFormRow
