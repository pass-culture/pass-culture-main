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
        className={styles['input-beginning-date']}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('eventDatetime')}
      />
      <TimePicker
        smallLabel
        label="Horaire"
        className={styles['input-beginning-time']}
        name="beginningTime"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('eventTime')}
      />
      <TextInput
        smallLabel
        name="price"
        label="Prix"
        className={styles['input-price']}
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
        openingDateTime={today}
        disabled={readOnlyFields.includes('bookingLimitDatetime')}
      />
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

export default StockEventForm
