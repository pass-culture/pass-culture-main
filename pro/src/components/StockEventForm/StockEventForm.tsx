import cn from 'classnames'
import { isAfter } from 'date-fns'
import { useFormikContext } from 'formik'
import React from 'react'

import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import styles from './StockEventForm.module.scss'
import { IStockEventFormValues } from './types'

export interface IStockEventFormProps {
  today: Date
  readOnlyFields?: string[]
  fieldPrefix?: string
}

const phoneNumberRegex = (name: string): number => {
  const rx = /\[(.*)\]/g
  const match = rx.exec(name)
  if (match === null) {
    throw Error(`Unable to found stock for field name: ${name}`)
  }
  return parseInt(match[1], 10)
}

const StockEventForm = ({
  today,
  readOnlyFields = [],
  fieldPrefix = '',
}: IStockEventFormProps): JSX.Element => {
  const { values, setFieldValue, setTouched } = useFormikContext<{
    stocks: IStockEventFormValues[]
  }>()
  const onChangeBeginningDate = (name: string, date: Date | null) => {
    const stockIndex = phoneNumberRegex(name)
    const stockBookingLimitDatetime =
      values.stocks[stockIndex].bookingLimitDatetime
    if (
      date &&
      (stockBookingLimitDatetime === null ||
        isAfter(date, stockBookingLimitDatetime))
    ) {
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
        name={`${fieldPrefix}beginningDate`}
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
        name={`${fieldPrefix}beginningTime`}
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('beginningTime')}
      />
      <TextInput
        smallLabel
        name={`${fieldPrefix}price`}
        label="Prix"
        className={cn(styles['input-price'], styles['field-layout-align-self'])}
        placeholder="Ex: 20€"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
      />
      <DatePicker
        smallLabel
        name={`${fieldPrefix}bookingLimitDatetime`}
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
        name={`${fieldPrefix}quantity`}
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
