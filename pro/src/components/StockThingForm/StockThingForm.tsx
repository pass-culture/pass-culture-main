import { useFormikContext } from 'formik'
import React from 'react'

import { DatePicker, TextInput } from 'ui-kit'

import styles from './StockThingForm.module.scss'
import { IStockThingFormValues } from './types'

export interface IStockThingFormProps {
  today: Date
  readOnlyFields?: string[]
  showExpirationDate?: boolean
}
const StockThingForm = ({
  today,
  showExpirationDate = false,
  readOnlyFields = [],
}: IStockThingFormProps): JSX.Element => {
  const getMaximumBookingDatetime = (date: Date | undefined) => {
    if (date == undefined) return undefined
    const result = new Date(date)
    result.setDate(result.getDate() - 7)
    return result
  }
  const values = useFormikContext().values as IStockThingFormValues
  const maxDateTime = values.activationCodesExpirationDatetime ?? undefined
  return (
    <>
      <TextInput
        smallLabel
        name="price"
        label="Prix"
        placeholder="Ex: 20€"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
      />
      <DatePicker
        smallLabel
        name="bookingLimitDatetime"
        label="Date limite de réservation"
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        maxDateTime={getMaximumBookingDatetime(maxDateTime)}
        openingDateTime={today}
        disabled={readOnlyFields.includes('bookingLimitDatetime')}
      />

      {showExpirationDate && (
        <DatePicker
          smallLabel
          name="activationCodesExpirationDatetime"
          label="Date d'expiration"
          classNameFooter={styles['field-layout-footer']}
          disabled={true}
        />
      )}
      <TextInput
        smallLabel
        name="quantity"
        label="Quantité"
        placeholder="Illimité"
        className={styles['input-quantity']}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('quantity')}
      />
    </>
  )
}

export default StockThingForm
