import * as yup from 'yup'

import { phoneValidationSchema } from 'ui-kit/form/PhoneNumberInput/phoneValidationSchema'

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
