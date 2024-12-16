import { StringSchema } from 'yup'

import { SelectOption } from 'commons/custom_types/form'

import { parseAndValidateFrenchPhoneNumber } from './parseAndValidateFrenchPhoneNumber'

export const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

export const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return false
  }
  try {
    parseAndValidateFrenchPhoneNumber(phone)
  } catch {
    return false
  }
  return true
}

export const isPasswordValid = (password: string | undefined): boolean => {
  if (!password) {
    return false
  }
  if (password.length < 12) {
    return false
  }
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumber = /[0-9]/.test(password)
  const hasSymbole = /[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(password)
  if (hasUpperCase && hasLowerCase && hasNumber && hasSymbole) {
    return true
  }
  return false
}

const PasswordValidationCheck = {
  LENGTH: 'LENGTH',
  UPPER_CASE: 'UPPER_CASE',
  LOWER_CASE: 'LOWER_CASE',
  NUMBER: 'NUMBER',
  SYMBOLE: 'SYMBOLE',
} as const

export const getPasswordRuleLabel = (value: string) => {
  switch (value) {
    case PasswordValidationCheck.LENGTH:
      return '12 caractères'
    case PasswordValidationCheck.UPPER_CASE:
      return '1 majuscule'
    case PasswordValidationCheck.LOWER_CASE:
      return '1 minuscule'
    case PasswordValidationCheck.NUMBER:
      return '1 chiffre'
    case PasswordValidationCheck.SYMBOLE:
      return '1 caractère spécial (!@#$%^&*...)'
    default:
      return ''
  }
}

export const passwordValidationStatus = (
  password: string | undefined
): { [key: string]: boolean } => {
  const errors: { [key: string]: boolean } = {}
  if (password) {
    errors[PasswordValidationCheck.LENGTH] = password.length < 12
    const hasUpperCase = /[A-Z]/.test(password)
    errors[PasswordValidationCheck.UPPER_CASE] = !hasUpperCase
    const hasLowerCase = /[a-z]/.test(password)
    errors[PasswordValidationCheck.LOWER_CASE] = !hasLowerCase
    const hasNumber = /[0-9]/.test(password)
    errors[PasswordValidationCheck.NUMBER] = !hasNumber
    const hasSymbole = /[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(password)
    errors[PasswordValidationCheck.SYMBOLE] = !hasSymbole
  }
  return errors
}

export const oneOfSelectOption = (
  field: StringSchema,
  options: SelectOption[]
) =>
  field.oneOf(
    options.map(({ value }) => String(value)).concat(['']),
    ({ value }) => `"${String(value)} " n’est pas une valeur valide de la liste`
  )
