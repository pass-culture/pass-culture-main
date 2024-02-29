import * as yup from 'yup'

import { isOneTrue } from 'core/shared/utils/validation'

export const validationSchema = yup.object().shape({
  accessibility: yup.object().when('isVenueVirtual', {
    is: false,
    then: (schema) =>
      schema
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
  }),
  addressAutocomplete: yup
    .string()
    .required('Veuillez sélectionner une adresse parmi les suggestions'),
  bookingEmail: yup
    .string()
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com')
    .required('Veuillez renseigner une adresse email'),
  name: yup
    .string()
    .required(`Veuillez renseigner la raison sociale de votre lieu`),
  venueType: yup
    .string()
    .required('Veuillez sélectionner une activité principale'),
})
