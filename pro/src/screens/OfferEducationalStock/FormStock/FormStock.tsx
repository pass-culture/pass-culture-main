import { useFormikContext } from 'formik'
import React from 'react'

import { OfferEducationalStockFormValues } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { DatePicker, TextArea, TextInput, TimePicker } from 'ui-kit'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  DETAILS_PRICE_LABEL,
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
      <FormLayout.Row inline>
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
      </FormLayout.Row>
      <FormLayout.Row>
        <TextArea
          className={styles['price-details']}
          countCharacters
          isOptional
          label={DETAILS_PRICE_LABEL}
          maxLength={1000}
          name="priceDetail"
          placeholder="Détaillez ici ce que comprend votre prix total"
        />
      </FormLayout.Row>
    </>
  )
}

export default FormStock
