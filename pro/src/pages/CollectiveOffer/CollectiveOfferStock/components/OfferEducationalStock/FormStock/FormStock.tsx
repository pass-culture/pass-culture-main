import { useFormikContext } from 'formik'
import React from 'react'

import {
  OfferEducationalStockFormValues,
  Mode,
} from 'commons/core/OfferEducational/types'
import { isDateValid } from 'commons/utils/date'
import { FormLayout } from 'components/FormLayout/FormLayout'
import strokeCollaborator from 'icons/stroke-collaborator.svg'
import strokeEuroIcon from 'icons/stroke-euro.svg'
import { DatePicker } from 'ui-kit/form/DatePicker/DatePicker'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'

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
  canEditDiscount: boolean
  canEditDates: boolean
  preventPriceIncrease: boolean
}

export const FormStock = ({
  mode,
  canEditDiscount,
  canEditDates,
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
    }
  }

  return (
    <FormLayout.Row inline className={styles['layout-row']}>
      <DatePicker
        disabled={!canEditDates}
        label={START_DATE_LABEL}
        minDate={new Date()}
        name="startDatetime"
        onChange={handleStartDatetimeChange}
        className={styles['input-date']}
        hideAsterisk={true}
      />
      <DatePicker
        disabled={!canEditDates}
        label={END_DATE_LABEL}
        minDate={minEndDatetime}
        name="endDatetime"
        className={styles['input-date']}
        help={
          'Le remboursement de votre offre sera effectué 2 à 3 semaines après la fin de votre évènement.'
        }
        hideAsterisk={true}
      />
      <TimePicker
        disabled={!canEditDates}
        label={EVENT_TIME_LABEL}
        name="eventTime"
        className={styles['custom-field-layout']}
        hideAsterisk={true}
      />
      <TextInput
        disabled={!canEditDiscount}
        label={NUMBER_OF_PLACES_LABEL}
        name="numberOfPlaces"
        type="number"
        hasLabelLineBreak={false}
        rightIcon={strokeCollaborator}
        classNameInput={styles['input-custom-width']}
        hideAsterisk={true}
      />
      <TextInput
        disabled={!canEditDiscount}
        label={TOTAL_PRICE_LABEL}
        name="totalPrice"
        step={0.01} // allow user to enter a price with cents
        min={0}
        type="number"
        rightIcon={strokeEuroIcon}
        classNameInput={styles['input-custom-width']}
        hideAsterisk={true}
      />
    </FormLayout.Row>
  )
}
