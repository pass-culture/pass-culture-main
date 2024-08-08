import classNames from 'classnames'
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
  END_DATE_LABEL,
  EVENT_TIME_LABEL,
  NUMBER_OF_PLACES_LABEL,
  START_DATE_LABEL,
  TOTAL_PRICE_LABEL,
} from '../constants/labels'

import styles from './FormStock.module.scss'

export interface FormStockProps {
  mode: Mode
  disablePriceAndParticipantInputs: boolean
  preventPriceIncrease: boolean
}

export const FormStock = ({
  mode,
  disablePriceAndParticipantInputs,
}: FormStockProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalStockFormValues>()

  const minEndDatetime = isDateValid(values.startDatetime)
    ? new Date(values.startDatetime)
    : new Date()

  async function handleStartDatetimeChange(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    if (mode === Mode.EDITION || mode === Mode.CREATION) {
      if (
        !isDateValid(values.endDatetime) ||
        values.endDatetime < event.target.value
      ) {
        await setFieldValue('endDatetime', event.target.value)
      }

      if (
        !isDateValid(values.bookingLimitDatetime) ||
        values.bookingLimitDatetime > event.target.value
      ) {
        await setFieldValue('bookingLimitDatetime', event.target.value)
      }
    }
  }

  return (
    <FormLayout.Row inline className={styles['layout-row']}>
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={START_DATE_LABEL}
        minDate={new Date()}
        name="startDatetime"
        onChange={handleStartDatetimeChange}
        className={classNames(
          styles['input-date'],
          styles['custom-field-layout']
        )}
      />
      <DatePicker
        disabled={mode === Mode.READ_ONLY}
        label={END_DATE_LABEL}
        minDate={minEndDatetime}
        name="endDatetime"
        className={classNames(
          styles['input-date'],
          styles['custom-field-layout']
        )}
      />
      <TimePicker
        disabled={mode === Mode.READ_ONLY}
        label={EVENT_TIME_LABEL}
        name="eventTime"
        className={styles['custom-field-layout']}
      />
      <TextInput
        disabled={disablePriceAndParticipantInputs}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        type="number"
        hasLabelLineBreak={false}
        rightIcon={strokeCollaborator}
        className={styles['custom-field-layout']}
        classNameInput={styles['input-custom-width']}
      />
      <TextInput
        disabled={disablePriceAndParticipantInputs}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        step={0.01} // allow user to enter a price with cents
        type="number"
        rightIcon={strokeEuroIcon}
        className={styles['custom-field-layout']}
        classNameInput={styles['input-custom-width']}
      />
    </FormLayout.Row>
  )
}
