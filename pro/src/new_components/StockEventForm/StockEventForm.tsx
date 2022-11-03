import cn from 'classnames'
import React from 'react'

import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import styles from './StockEventForm.module.scss'

export interface IStockEventFormProps {
  today: Date
  readOnlyFields?: string[]
}

const StockEventForm = ({
  today,
  readOnlyFields = [],
}: IStockEventFormProps): JSX.Element => {
  return (
    <>
      <DatePicker
        smallLabel
        name="beginningDate"
        label="Date"
        className={styles['field-layout-align-self']}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('eventDatetime')}
      />
      <TimePicker
        smallLabel
        label="Horaire"
        className={cn(
          styles['input-beginning-time'],
          styles['field-layout-align-self']
        )}
        name="beginningTime"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('eventTime')}
      />
      <TextInput
        smallLabel
        name="price"
        label="Prix"
        className={cn(styles['input-price'], styles['field-layout-align-self'])}
        placeholder="Ex: 20€"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('price')}
      />
      <DatePicker
        smallLabel
        name="bookingLimitDatetime"
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
        name="quantity"
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
