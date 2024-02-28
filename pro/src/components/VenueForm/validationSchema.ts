import * as yup from 'yup'

import { urlRegex } from 'core/shared'
import { isPhoneValid } from 'core/shared/utils/validation'

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

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
  addressAutocomplete: yup.string().when('isVenueVirtual', {
    is: false,
    then: (schema) =>
      schema.required(
        'Veuillez sélectionner une adresse parmi les suggestions'
      ),
  }),
  bookingEmail: yup
    .string()
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com')
    .when('isVenueVirtual', {
      is: false,
      then: (schema) =>
        schema.required('Veuillez renseigner une adresse email'),
    }),
  email: yup
    .string()
    .nullable()
    .email('Veuillez renseigner un email valide, exemple : mail@exemple.com'),
  isVenueVirtual: yup.boolean(),
  name: yup
    .string()
    .required(`Veuillez renseigner la raison sociale de votre lieu`),
  phoneNumber: yup
    .string()
    .nullable()
    .test({
      name: 'is-phone-valid',
      message:
        'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
      test: (phone?: string | null) => {
        /* istanbul ignore next: DEBT, TO FIX */
        return phone ? isPhoneValid(phone) : true
      },
    }),
  venueType: yup
    .string()
    .required('Veuillez sélectionner une activité principale'),

  webSite: yup
    .string()
    .nullable()
    .test({
      name: 'matchWebsiteUrl',
      message: 'Veuillez renseigner une URL valide. Ex : https://exemple.com',
      test: (url?: string | null) => {
        /* istanbul ignore next: DEBT, TO FIX */
        return url ? url.match(urlRegex) !== null : true
      },
    }),
})
