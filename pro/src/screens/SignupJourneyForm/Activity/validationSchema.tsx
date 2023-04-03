import * as yup from 'yup'

import { Target } from 'apiClient/v1'

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
    .string()
    .oneOf(
      Object.values(Target),
      'Veuillez sélectionner une des réponses ci-dessus'
    )
    .required('Veuillez sélectionner une des réponses ci-dessus'),
})
