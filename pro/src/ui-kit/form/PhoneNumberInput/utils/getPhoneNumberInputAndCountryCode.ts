import type { CountryCode } from 'libphonenumber-js'

import { parseAndValidateFrenchPhoneNumber } from 'core/shared/utils/parseAndValidateFrenchPhoneNumber'

import { PHONE_CODE_COUNTRY_CODE_OPTIONS } from '../constants'

type PhoneNumberInputAndCountryCode = {
  inputValue: string
  countryCode: CountryCode
}
const DEFAULT_VALUES: PhoneNumberInputAndCountryCode = {
  inputValue: '',
  countryCode: 'FR',
}

export const getPhoneNumberInputAndCountryCode = (
  phoneNumber?: string
): PhoneNumberInputAndCountryCode => {
  if (!phoneNumber) {
    return DEFAULT_VALUES
  }

  const phoneNumberWithCountryCode =
    parseAndValidateFrenchPhoneNumber(phoneNumber)

  if (phoneNumberWithCountryCode?.number) {
    const countryCode = PHONE_CODE_COUNTRY_CODE_OPTIONS.find(
      option =>
        option.label === `+${phoneNumberWithCountryCode.countryCallingCode}`
    )?.value as CountryCode

    return {
      inputValue: phoneNumberWithCountryCode.nationalNumber,
      countryCode,
    }
  }

  return DEFAULT_VALUES
}
