import {
  DEFAULT_FORM_VALUES,
  EXTRA_DATA_FIELDS,
  TEXT_INPUT_DEFAULT_VALUE,
} from '../_constants'

import { OFFER_WITHDRAWAL_TYPE_OPTIONS } from 'core/Offers'

export const serializeSubmitValues = (
  formValues,
  offerFormFields,
  readOnlyFields,
  receiveNotificationEmails
) => {
  const editableFields = offerFormFields.filter(
    field => !readOnlyFields.includes(field)
  )

  const submittedValuesAccumulator = editableFields.some(editableField =>
    EXTRA_DATA_FIELDS.includes(editableField)
  )
    ? { extraData: null }
    : {}

  const submittedValues = editableFields.reduce(
    (submittedValues, fieldName) => {
      if (!EXTRA_DATA_FIELDS.includes(fieldName)) {
        const fieldValue =
          formValues[fieldName] === TEXT_INPUT_DEFAULT_VALUE
            ? null
            : formValues[fieldName]
        submittedValues = {
          ...submittedValues,
          [fieldName]: fieldValue,
        }
      } else if (formValues[fieldName] !== DEFAULT_FORM_VALUES[fieldName]) {
        submittedValues.extraData = {
          ...submittedValues.extraData,
          [fieldName]: formValues[fieldName],
        }
      }

      return submittedValues
    },
    submittedValuesAccumulator
  )

  // front should check categoryId but do not send to backend
  delete submittedValues.categoryId

  if (!receiveNotificationEmails) {
    submittedValues.bookingEmail = null
  }

  if (
    submittedValues.withdrawalType &&
    submittedValues.withdrawalType === OFFER_WITHDRAWAL_TYPE_OPTIONS.NO_TICKET
  ) {
    submittedValues.withdrawalDelay = null
  }

  return submittedValues
}
