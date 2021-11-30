import React from 'react'

import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

import styles from './FormStock.module.scss'

const EACOfferStockCreationType = (): JSX.Element => {
  return (
    <>
      <DatePicker
        className={styles['form-field']}
        label={EVENT_DATE_LABEL}
        name="eventDate"
      />
      <TimePicker
        className={styles['form-field']}
        label={EVENT_TIME_LABEL}
        name="eventTime"
      />
      <TextInput
        className={styles['form-field']}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        placeholder="Ex : 30"
        type="number"
      />
      <TextInput
        className={styles['form-field']}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        placeholder="Ex : 200€"
        type="number"
      />
      <DatePicker
        className={styles['form-field']}
        label={BOOKING_LIMIT_DATETIME_LABEL}
        name="bookingLimitDatetime"
      />
    </>
  )
}

export default EACOfferStockCreationType
