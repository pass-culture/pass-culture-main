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
