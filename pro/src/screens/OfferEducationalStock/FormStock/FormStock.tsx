import { useFormikContext } from 'formik'
import React from 'react'

import { Mode, OfferEducationalStockFormValues } from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { DatePicker, TextInput, TimePicker } from 'ui-kit'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

interface IFormStockProps {
  mode: Mode
}

const FormStock = ({ mode }: IFormStockProps): JSX.Element => {
  const { values } = useFormikContext<OfferEducationalStockFormValues>()

  return (
    <FormLayout.Row inline>
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_DATE_LABEL}
        minDateTime={new Date()}
        name="eventDate"
        smallLabel
      />
      <TimePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_TIME_LABEL}
        name="eventTime"
        smallLabel
      />
      <TextInput
        disabled={mode === Mode.READ_ONLY}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        placeholder="Ex : 30"
        smallLabel
        type="number"
      />
      <TextInput
        disabled={mode === Mode.READ_ONLY}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        placeholder="Ex : 200€"
        smallLabel
        step={0.01} // allow user to enter a price with cents
        type="number"
      />
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={BOOKING_LIMIT_DATETIME_LABEL}
        maxDateTime={values.eventDate ? values.eventDate : undefined}
        name="bookingLimitDatetime"
        smallLabel
      />
    </FormLayout.Row>
  )
}

export default FormStock
