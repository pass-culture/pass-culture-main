import { parsePhoneNumberFromString } from 'libphonenumber-js'
import type { CountryCode } from 'libphonenumber-js'

import { parseAndValidateFrenchPhoneNumber } from 'core/shared/utils/parseAndValidateFrenchPhoneNumber'

import { PHONE_CODE_COUNTRY_CODE_OPTIONS } from '../constants'

export const getPhoneNumberValues = (
  phoneNumber: string
): { inputValue: string; countryCode: CountryCode } => {
  const phoneNumberWithCountryCode =
    parseAndValidateFrenchPhoneNumber(phoneNumber)

  if (phoneNumberWithCountryCode?.number) {
    for (const option of PHONE_CODE_COUNTRY_CODE_OPTIONS) {
      const parsedPhoneNumber = parsePhoneNumberFromString(
        phoneNumberWithCountryCode.number,
        option.value
      )

      if (parsedPhoneNumber?.isValid()) {
        return {
          inputValue: parsedPhoneNumber.nationalNumber,
          countryCode: parsedPhoneNumber.country as CountryCode,
        }
      }
    }
  }

  return { inputValue: '', countryCode: 'FR' }
}
