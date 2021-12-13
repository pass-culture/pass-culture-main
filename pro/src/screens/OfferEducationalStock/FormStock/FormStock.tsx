import { useFormikContext } from 'formik'
import React from 'react'

import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import { OfferEducationalStockFormValues } from '../../../core/OfferEducationalStock/types'
import {
  BOOKING_LIMIT_DATETIME_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

import styles from './FormStock.module.scss'

const EACOfferStockCreationType = ({
  isEditable,
}: {
  isEditable: boolean
}): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalStockFormValues>()
  return (
    <>
      <DatePicker
        className={styles['form-field']}
        disabled={!isEditable}
        label={EVENT_DATE_LABEL}
        minDateTime={new Date()}
        name="eventDate"
        smallLabel
      />
      <TimePicker
        className={styles['form-field']}
        disabled={!isEditable}
        label={EVENT_TIME_LABEL}
        name="eventTime"
        smallLabel
      />
      <TextInput
        className={styles['form-field']}
        disabled={!isEditable}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        placeholder="Ex : 30"
        smallLabel
        type="number"
      />
      <TextInput
        className={styles['form-field']}
        disabled={!isEditable}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        placeholder="Ex : 200€"
        smallLabel
        type="number"
      />
      <DatePicker
        className={styles['form-field']}
        disabled={!isEditable}
        label={BOOKING_LIMIT_DATETIME_LABEL}
        maxDateTime={new Date(values.eventDate)}
        name="bookingLimitDatetime"
        smallLabel
      />
    </>
  )
}

export default EACOfferStockCreationType
