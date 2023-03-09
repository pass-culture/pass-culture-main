import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { isPasswordValid } from 'core/shared/utils/validation'

const passwordErrorMessage = `Votre mot de passe doit contenir au moins :
      - 12 caractères
      - Un chiffre
      - Une majuscule et une minuscule
      - Un caractère spécial
`

export const validationSchema = (newOnboardingActive: boolean) =>
  yup.object().shape({
    email: yup
      .string()
      .max(120)
      .email('Veuillez renseigner un e-mail valide')
      .required('Veuillez renseigner une adresse e-mail'),
    password: yup
      .string()
      .required('Veuillez renseigner un mot de passe')
      .test('isPasswordValid', passwordErrorMessage, isPasswordValid),
    lastName: yup.string().max(128).required('Veuillez renseigner votre nom'),
    firstName: yup
      .string()
      .max(128)
      .required('Veuillez renseigner votre prénom'),
    // TODO (mageoffray, 2022-05-12): Create a generic validator method for phone validation
    phoneNumber: yup
      .string()
      .min(10, 'Veuillez renseigner au moins 10 chiffres')
      .max(20, 'Veuillez renseigner moins de 20 chiffres')
      .required('Veuillez renseigner votre numéro de téléphone')
      .test(
        'isPhoneValid',
        'Votre numéro de téléphone n’est pas valide',
        value => {
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
    siren: yup
      .string()
      .test(
        'sirenMaybeRequired',
        'Veuillez renseigner le siren de votre entreprise',
        value => {
          return newOnboardingActive || Boolean(value)
        }
      )
      .min(9, 'Le SIREN doit comporter 9 caractères.')
      .max(11, 'Le SIREN doit comporter 9 caractères.'),
  })
