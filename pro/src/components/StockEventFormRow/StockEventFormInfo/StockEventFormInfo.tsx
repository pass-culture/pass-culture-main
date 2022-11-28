import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import { IStockEventFormValues } from 'components/StockEventForm'
import { TextInput } from 'ui-kit'

import styles from './StockEventFormInfo.module.scss'

interface IStockEventFormInfoProps {
  className?: string
  index: number
}
const StockEventFormInfo = ({
  index,
  className,
}: IStockEventFormInfoProps): JSX.Element => {
  const { values } = useFormikContext<{ stocks: IStockEventFormValues[] }>()
  const { remainingQuantity, bookingsQuantity } = values.stocks[index]
  return (
    <div className={cn(styles['stock-form-info'], className)}>
      <TextInput
        name={`stocks[${index}]remainingQuantity`}
        value={
          remainingQuantity === 'unlimited' ? 'Illimité' : remainingQuantity
        }
        readOnly
        label="Stock restant"
        smallLabel
        classNameFooter={styles['field-layout-footer']}
      />
      <TextInput
        name={`stocks[${index}]bookingsQuantity`}
        value={bookingsQuantity || 0}
        readOnly
        label="Réservations"
        smallLabel
        classNameFooter={styles['field-layout-footer']}
      />
    </div>
  )
}

export default StockEventFormInfo
