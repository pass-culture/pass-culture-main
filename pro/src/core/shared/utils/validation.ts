import { parsePhoneNumberFromString } from 'libphonenumber-js'

export const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return false
  }
  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}
