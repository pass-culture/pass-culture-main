import cn from 'classnames'
import { isAfter } from 'date-fns'
import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import { IconEuroGrey } from 'icons'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import styles from './StockEventForm.module.scss'
import { IStockEventFormValues } from './types'

export interface IStockEventFormProps {
  today: Date
  readOnlyFields?: string[]
  stockIndex: number
}

const StockEventForm = ({
  today,
  readOnlyFields = [],
  stockIndex,
}: IStockEventFormProps): JSX.Element => {
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()
  const [showCurrencyIcon, showShowCurrencyIcon] = useState<boolean>(
    values.stocks[stockIndex].price.length > 0
  )
  useEffect(() => {
    showShowCurrencyIcon(values.stocks[stockIndex].price.length > 0)
  }, [values.stocks[stockIndex].price])

  const onChangeBeginningDate = (_name: string, date: Date | null) => {
    const stockBookingLimitDatetime =
      values.stocks[stockIndex].bookingLimitDatetime
    if (stockBookingLimitDatetime === null) {
      return
    }
    if (date && isAfter(stockBookingLimitDatetime, date)) {
      setTouched({
        [`stocks[${stockIndex}]bookingLimitDatetime`]: true,
      })
      setFieldValue(`stocks[${stockIndex}]bookingLimitDatetime`, date)
    }
  }

  return (
    <>
      <DatePicker
        smallLabel
        name={`stocks[${stockIndex}]beginningDate`}
        label="Date"
        className={styles['field-layout-align-self']}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('beginningDate')}
        onChange={onChangeBeginningDate}
      />
      <TimePicker
        smallLabel
        label="Horaire"
        className={cn(
          styles['input-beginning-time'],
          styles['field-layout-align-self']
        )}
        name={`stocks[${stockIndex}]beginningTime`}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('beginningTime')}
      />
      <TextInput
        smallLabel
        name={`stocks[${stockIndex}]price`}
        label="Prix"
        className={cn(styles['input-price'], styles['field-layout-align-self'])}
        placeholder="Ex: 20€"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
        rightIcon={() => (showCurrencyIcon ? <IconEuroGrey /> : null)}
      />
      <DatePicker
        smallLabel
        name={`stocks[${stockIndex}]bookingLimitDatetime`}
        label="Date limite de réservation"
        className={cn(
          styles['input-bookingLimitDatetime'],
          styles['field-layout-align-self']
        )}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('bookingLimitDatetime')}
      />
      <TextInput
        smallLabel
        name={`stocks[${stockIndex}]quantity`}
        label="Quantité"
        placeholder="Illimité"
        className={cn(
          styles['input-quantity'],
          styles['field-layout-align-self']
        )}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('quantity')}
      />
    </>
  )
}

export default StockEventForm
