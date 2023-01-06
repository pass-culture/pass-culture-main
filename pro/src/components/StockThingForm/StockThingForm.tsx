import cn from 'classnames'
import { useFormikContext } from 'formik'
import React from 'react'

import { IcoEuro } from 'icons'
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
  const { values, setFieldValue } = useFormikContext<IStockThingFormValues>()
  const maxDateTime = values.activationCodesExpirationDatetime ?? undefined

  const onChangeQuantity = (event: React.ChangeEvent<HTMLInputElement>) => {
    const quantity = event.target.value
    let remainingQuantity: number | string =
      // No need to test
      /* istanbul ignore next */
      Number(quantity || 0) - Number(values.bookingsQuantity || 0)

    if (quantity === '') {
      remainingQuantity = 'unlimited'
    }

    setFieldValue(`remainingQuantity`, remainingQuantity)
    setFieldValue(`quantity`, quantity)
  }

  return (
    <>
      <TextInput
        smallLabel
        name="price"
        label="Prix"
        className={cn({
          [styles['input-price']]: !showExpirationDate,
        })}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
        type="number"
        rightIcon={() => <IcoEuro tabIndex={-1} />}
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
        onChange={onChangeQuantity}
      />
    </>
  )
}

export default StockThingForm
