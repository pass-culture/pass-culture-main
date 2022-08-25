import { parseAndValidateFrenchPhoneNumber } from './parseAndValidateFrenchPhoneNumber'

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
  if (password.length <= 12) return false
  const hasUpperCase = /[A-Z]/.test(password)
  const hasLowerCase = /[a-z]/.test(password)
  const hasNumber = /[0-9]/.test(password)
  const hasSymbole = /[!"#$%&'()*+,-./:;<=>?@[\\^_`{|}~\]]/.test(password)
  if (hasUpperCase && hasLowerCase && hasNumber && hasSymbole) {
    return true
  }
  return false
}
