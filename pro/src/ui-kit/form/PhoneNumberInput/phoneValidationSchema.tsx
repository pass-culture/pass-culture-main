import * as yup from 'yup'
import { parsePhoneNumberFromString } from 'libphonenumber-js'

export const validationSchema = ({
  isPhoneRequired,
}: {
  isPhoneRequired: boolean
}) => {
  return yup.object().shape({
    phoneNumber: yup
      .string()
      .min(10, 'Veuillez renseigner au moins 10 chiffres')
      .max(20, 'Veuillez renseigner moins de 20 chiffres')
      .when([], {
        is: () => isPhoneRequired,
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
  })
}
