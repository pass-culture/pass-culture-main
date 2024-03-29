import * as yup from 'yup'

export const validationSchema = yup.object().shape({
  venueTypeCode: yup
    .string()
    .required('Veuillez sélectionner une activité principale'),
  socialUrls: yup
    .array()
    .of(
      yup
        .string()
        .url('Veuillez renseigner une URL valide. Ex : https://exemple.com')
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
