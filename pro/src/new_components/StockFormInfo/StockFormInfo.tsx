import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import { IStockThingFormValues } from 'new_components/StockThingForm'
import { TextInput } from 'ui-kit'

import styles from './StockFormInfo.module.scss'

interface IStockFormInfoProps {
  className?: string
}
const StockFormInfo = ({ className }: IStockFormInfoProps): JSX.Element => {
  const {
    values: { bookingsQuantity, remainingQuantity },
  } = useFormikContext<IStockThingFormValues>()

  return (
    <div className={cn(styles['stock-form-info'], className)}>
      <TextInput
        name="availableStock"
        value={remainingQuantity || 'Illimité'}
        readOnly
        label="Stock restant"
        smallLabel
        classNameFooter={styles['field-layout-footer']}
      />
      <TextInput
        name="bookingsQuantity"
        value={bookingsQuantity || 0}
        readOnly
        label="Réservations"
        smallLabel
        classNameFooter={styles['field-layout-footer']}
      />
    </div>
  )
}

export default StockFormInfo
