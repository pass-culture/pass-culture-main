import { createValidateRequiredField } from 'react-final-form-utils'

const getRequiredValidate = (required, type) => {
  const requiredIsAFunction = required && typeof required === 'function'
  const errorMessage = 'Ce champ est obligatoire'
  const validateRequiredField = createValidateRequiredField(errorMessage, type)
  const defaultRequiredValidate = (required && validateRequiredField) || undefined
  const requiredValidate = requiredIsAFunction ? required : defaultRequiredValidate
  return requiredValidate
}

export default getRequiredValidate
