import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import { IconEuroGrey } from 'icons'
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
    if (date == undefined) {
      return undefined
    }
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
        className={cn({
          [styles['input-price']]: !showExpirationDate,
        })}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
        type="number"
        rightIcon={
          values.price ? () => <IconEuroGrey tabIndex={-1} /> : () => <></>
        }
      />
      <DatePicker
        smallLabel
        name="bookingLimitDatetime"
        label="Date limite de réservation"
        className={cn({
          [styles['input-booking-limit-datetime']]: !showExpirationDate,
        })}
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
          className={styles['input-activation-code']}
          classNameFooter={styles['field-layout-footer']}
          disabled={true}
        />
      )}
      <TextInput
        smallLabel
        name="quantity"
        label="Quantité"
        placeholder="Illimité"
        className={cn({
          [styles['input-quantity']]: !showExpirationDate,
        })}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('quantity')}
        type="number"
        hasDecimal={false}
      />
    </>
  )
}

export default StockThingForm
