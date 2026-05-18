import parsePhoneNumberFromString, {
  type PhoneNumber,
} from 'libphonenumber-js/max'
import * as yup from 'yup'

import {
  PHONE_EXAMPLE_MAP,
  type PlusString,
} from '@/commons/core/Phone/constants'
import { isCountryCodeHandledByPassCulture } from '@/commons/core/Phone/utils/isCountryCodeHandledByPassCulture'
import { stripPhoneSeparators } from '@/commons/utils/stripPhoneSeparators'

const validateAndParseFrenchPhoneNumber = (
  phoneNumber: string
): PhoneNumber => {
  const parsedPhone = parsePhoneNumberFromString(phoneNumber, 'FR')

  if (parsedPhone === undefined) {
    throw new Error(`Veuillez renseigner un numéro de téléphone valide`)
  }

  const countryCode: PlusString = `+${parsedPhone?.countryCallingCode}`

  if (!isCountryCodeHandledByPassCulture(countryCode)) {
    throw new Error('Ce numéro de téléphone n’est pas pris en charge')
  }

  // Ensure phoneNumber is valid and only contains digits and spaces
  // because libphonenumber-js considers this is valid : "+33612345678foobarbaz" …
  if (!parsedPhone.isValid() || /[^\d+\s]/.test(phoneNumber)) {
    const exampleValidPhoneNumber = PHONE_EXAMPLE_MAP[countryCode]
    throw new Error(
      `Veuillez renseigner un numéro de téléphone valide, exemple : ${exampleValidPhoneNumber}`
    )
  }

  return parsedPhone
}

/**
 * Validates and parses a phone number for Pass Culture handled country codes.
 *
 * @returns {yup.StringSchema} A Yup validation schema for phone numbers.
 *
 * @example
 * phoneNumberSchema() // optional phone number
 * phoneNumberSchema().nullable() // nullable phone number
 * phoneNumberSchema().required('Phone is required') // required phone number
 */
export const phoneNumberSchema = () => {
  return yup
    .string()
    .transform(stripPhoneSeparators)
    .test('isPhoneValid', function isPhoneValidWithErrorMessage(this: yup.TestContext, value:
      | string
      | null
      | undefined): boolean {
      if (!value) {
        return true
      }
      try {
        validateAndParseFrenchPhoneNumber(value)
        return true
      } catch (error) {
        throw this.createError({
          message:
            error instanceof Error
              ? error.message
              : 'Veuillez renseigner un numéro de téléphone valide',
        })
      }
    })
}
