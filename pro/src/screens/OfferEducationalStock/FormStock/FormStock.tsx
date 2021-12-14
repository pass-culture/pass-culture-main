import { useFormikContext } from 'formik'
import React from 'react'

import { OfferEducationalStockFormValues } from 'core/OfferEducational'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

import styles from './FormStock.module.scss'

const FormStock = ({
  isFormDisabled,
}: {
  isFormDisabled: boolean
}): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalStockFormValues>()
  return (
    <>
      <DatePicker
        className={styles['form-field']}
        disabled={isFormDisabled}
        label={EVENT_DATE_LABEL}
        minDateTime={new Date()}
        name="eventDate"
        smallLabel
      />
      <TimePicker
        className={styles['form-field']}
        disabled={isFormDisabled}
        label={EVENT_TIME_LABEL}
        name="eventTime"
        smallLabel
      />
      <TextInput
        className={styles['form-field']}
        disabled={isFormDisabled}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        placeholder="Ex : 30"
        smallLabel
        type="number"
      />
      <TextInput
        className={styles['form-field']}
        disabled={isFormDisabled}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        placeholder="Ex : 200€"
        smallLabel
        type="number"
      />
      <DatePicker
        className={styles['form-field']}
        disabled={isFormDisabled}
        label={BOOKING_LIMIT_DATETIME_LABEL}
        maxDateTime={values.eventDate ? values.eventDate : undefined}
        name="bookingLimitDatetime"
        smallLabel
      />
    </>
  )
}

export default FormStock
