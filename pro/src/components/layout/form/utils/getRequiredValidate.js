import { createValidateRequiredField } from 'utils/react-final-form'

const createValidateRequiredBooleanField = errorMessage => {
  return value => {
    if (value === true || value === false) return undefined
    return errorMessage
  }
}

const getRequiredValidate = (required, type) => {
  const requiredIsAFunction = required && typeof required === 'function'
  const errorMessage = 'Ce champ est obligatoire'
  const validateRequiredField =
    type === 'boolean'
      ? createValidateRequiredBooleanField(errorMessage)
      : createValidateRequiredField(errorMessage, type)
  const defaultRequiredValidate =
    (required && validateRequiredField) || undefined
  const requiredValidate = requiredIsAFunction
    ? required
    : defaultRequiredValidate
  return requiredValidate
}

export default getRequiredValidate
