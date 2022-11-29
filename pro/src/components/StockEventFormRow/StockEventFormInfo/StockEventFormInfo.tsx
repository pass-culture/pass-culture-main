import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import { IStockEventFormValues } from 'components/StockEventForm'
import { TextInput } from 'ui-kit'

import styles from './StockEventFormInfo.module.scss'

interface IStockEventFormInfoProps {
  className?: string
  stockIndex: number
}
const StockEventFormInfo = ({
  stockIndex,
  className,
}: IStockEventFormInfoProps): JSX.Element => {
  const { values } = useFormikContext<{ stocks: IStockEventFormValues[] }>()
  const { remainingQuantity, bookingsQuantity } = values.stocks[stockIndex]
  return (
    <div className={cn(styles['stock-form-info'], className)}>
      <TextInput
        name={`stocks[${stockIndex}]remainingQuantity`}
        value={
          remainingQuantity === 'unlimited' ? 'Illimité' : remainingQuantity
        }
        readOnly
        label="Stock restant"
        isLabelHidden={stockIndex !== 0}
        smallLabel
        classNameFooter={styles['field-layout-footer']}
      />
      <TextInput
        name={`stocks[${stockIndex}]bookingsQuantity`}
        value={bookingsQuantity || 0}
        readOnly
        label="Réservations"
        isLabelHidden={stockIndex !== 0}
        smallLabel
        classNameFooter={styles['field-layout-footer']}
      />
    </div>
  )
}

export default StockEventFormInfo
