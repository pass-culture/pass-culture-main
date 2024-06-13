import { useFormikContext } from 'formik'
import React from 'react'

import { FormLayout } from 'components/FormLayout/FormLayout'
import {
  OfferEducationalStockFormValues,
  Mode,
} from 'core/OfferEducational/types'
import strokeCollaborator from 'icons/stroke-collaborator.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { isDateValid } from 'utils/date'

import {
  BOOKING_LIMIT_DATETIME_LABEL,
  EVENT_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

import styles from './FormStock.module.scss'

export interface FormStockProps {
  mode: Mode
  disablePriceAndParticipantInputs: boolean
  preventPriceIncrease: boolean
  offerDateCreated: string
}

export const FormStock = ({
  mode,
  disablePriceAndParticipantInputs,
  offerDateCreated,
}: FormStockProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalStockFormValues>()

  return (
    <FormLayout.Row inline>
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_DATE_LABEL}
        minDate={new Date()}
        name="eventDate"
        smallLabel
        onChange={async (event) => {
          if (mode === Mode.EDITION) {
            await setFieldValue('bookingLimitDatetime', event.target.value)
          }
        }}
        className={styles['input-date']}
      />
      <TimePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_TIME_LABEL}
        name="eventTime"
      />
      <TextInput
        disabled={disablePriceAndParticipantInputs}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        placeholder="Ex : 30"
        type="number"
        hasLabelLineBreak={false}
        rightIcon={strokeCollaborator}
      />
      <TextInput
        disabled={disablePriceAndParticipantInputs}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        step={0.01} // allow user to enter a price with cents
        type="number"
        rightIcon={strokeEuroIcon}
      />
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={BOOKING_LIMIT_DATETIME_LABEL}
        hasLabelLineBreak={false}
        minDate={new Date(offerDateCreated)}
        maxDate={
          isDateValid(new Date(values.eventDate))
            ? new Date(values.eventDate)
            : undefined
        }
        name="bookingLimitDatetime"
        smallLabel
        isOptional
        className={styles['input-date']}
      />
    </FormLayout.Row>
  )
}
