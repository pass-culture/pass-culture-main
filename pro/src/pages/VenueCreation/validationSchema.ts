import * as yup from 'yup'

import { isOneTrue } from 'commons/core/shared/utils/validation'
import { emailSchema } from 'commons/utils/isValidEmail'

export const validationSchema = yup.object().shape({
  accessibility: yup
    .object()
    .test({
      name: 'is-one-true',
      message: 'Veuillez sélectionner au moins un critère d’accessibilité',
      test: isOneTrue,
    })
    .shape({
      mental: yup.boolean(),
      audio: yup.boolean(),
      visual: yup.boolean(),
      motor: yup.boolean(),
      none: yup.boolean(),
    }),
  addressAutocomplete: yup
    .string()
    .required('Veuillez sélectionner une adresse parmi les suggestions'),
  bookingEmail: yup
    .string()
    .test(emailSchema)
    .required('Veuillez renseigner une adresse email'),
  name: yup
    .string()
    .required(`Veuillez renseigner la raison sociale de votre lieu`),
  venueType: yup
    .string()
    .required('Veuillez sélectionner une activité principale'),
})
