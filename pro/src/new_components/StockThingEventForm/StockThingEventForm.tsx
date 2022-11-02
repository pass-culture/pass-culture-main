import React from 'react'

import { IStockThingFormProps } from 'new_components/StockThingForm/StockThingForm'
import styles from 'new_components/StockThingForm/StockThingForm.module.scss'
import {
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
} from 'screens/OfferEducationalStock/constants/labels'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

const StockThingEventForm = ({
  today,
  readOnlyFields = [],
}: IStockThingFormProps): JSX.Element => {
  return (
    <>
      <DatePicker
        smallLabel
        name="eventDatetime"
        label={EVENT_DATE_LABEL}
        classNameFooter={styles['field-layout-footer']}
        minDateTime={today}
        openingDateTime={today}
        disabled={readOnlyFields.includes('eventDatetime')}
      />
      <TimePicker
        smallLabel
        label={EVENT_TIME_LABEL}
        name="eventTime"
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

export default StockThingEventForm
