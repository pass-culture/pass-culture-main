import React from 'react'

import styles from 'new_components/StockThingForm/StockThingForm.module.scss'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

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
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('eventDatetime')}
      />
      <TimePicker
        smallLabel
        label="Horraire"
        name="beginningTime"
        classNameFooter={styles['field-layout-footer']}
        disabled={readOnlyFields.includes('eventTime')}
      />
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
