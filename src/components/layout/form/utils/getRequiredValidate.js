import { createValidateRequiredField } from 'react-final-form-utils'

const validateRequiredField = createValidateRequiredField(
  'Ce champ est obligatoire'
)

const getRequiredValidate = required => {
  const requiredIsAFunction = required && typeof required === 'function'
  const defaultRequiredValidate =
    (required && validateRequiredField) || undefined
  const requiredValidate = requiredIsAFunction
    ? required
    : defaultRequiredValidate
  return requiredValidate
}

export default getRequiredValidate
