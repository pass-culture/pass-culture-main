import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { emailSchema } from 'commons/utils/isValidEmail'
import { passwordValidationStatus } from 'ui-kit/formV2/PasswordInput/validation'

export const validationSchema = (newSignup: boolean) => {
  return yup.object().shape({
    email: yup
      .string()
      .test(emailSchema)
      .required('Veuillez renseigner une adresse email'),
    password: yup
      .string()
      .required('Veuillez renseigner un mot de passe')
      .test(
        'isPasswordValid',
        'Veuillez renseigner un mot de passe valide avec : ',
        (paswordValue) => {
          const errors = passwordValidationStatus(paswordValue)
          const hasError = Object.values(errors).some((error) => error)
          return !hasError
        }
      ),
    lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
    firstName: yup
      .string()
      .max(128)
      .required('Veuillez renseigner votre prénom'),
    phoneNumber: yup
      .string()
      .min(10, 'Veuillez renseigner au moins 10 chiffres')
      .max(20, 'Veuillez renseigner moins de 20 chiffres')
      .when([], {
        is: () => !newSignup,
        then: (schema) =>
          schema.required('Veuillez renseigner un numéro de téléphone'),
      })
      .test(
        'isPhoneValid',
        'Veuillez renseigner un numéro de téléphone valide, exemple : 612345678',
        // TODO (jm) : Create a standard util function that can be used here and everywhere else (other "validationSchema.ts" files that checks phone numbers format
        (value) => {
          if (!value) {
            return false
          }
          const phoneNumber = parsePhoneNumberFromString(value, 'FR')
          const isValid = phoneNumber?.isValid()
          if (!isValid) {
            return false
          }
          return true
        }
      ),
    contactOk: yup.string(),
  })
}
