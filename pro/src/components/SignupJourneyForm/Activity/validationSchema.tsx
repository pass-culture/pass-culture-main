import parsePhoneNumberFromString from 'libphonenumber-js'
import * as yup from 'yup'

const phoneValidationSchema = yup.object().shape({
  phoneNumber: yup
    .string()
    .min(10, 'Veuillez renseigner au moins 10 chiffres')
    .required('Veuillez renseigner un numéro de téléphone')
    .max(20, 'Veuillez renseigner moins de 20 chiffres')
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

export const validationSchema = (newSignup: boolean) => {
  const schema = yup.object().shape({
    venueTypeCode: yup
      .string()
      .required('Veuillez sélectionner une activité principale'),
    socialUrls: yup
      .array()
      .of(
        yup.object().shape({
          url: yup
            .string()
            .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
            .nullable(),
        })
      )
      .nullable(),
    targetCustomer: yup
      .object()
      .test({
        name: 'is-one-true',
        message: 'Veuillez sélectionner une des réponses ci-dessus',
        test: (values: Record<string, boolean>): boolean =>
          Object.values(values).includes(true),
      })
      .shape({
        individual: yup.boolean(),
        educational: yup.boolean(),
      })
      .required('Veuillez sélectionner une des réponses ci-dessus'),
  })
  if (newSignup) {
    return schema.concat(phoneValidationSchema)
  } else {
    return schema
  }
}
