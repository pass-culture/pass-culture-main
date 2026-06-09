import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { emailSchema } from '@/commons/utils/isValidEmail'

import { SiretOrCommentValidationSchema } from '../components/SiretOrCommentFields/validationSchema'

export const venueSettingsValidationSchema = yup
  .object()
  .shape({
    manuallySetAddress: yup.boolean().nullable(),
    addressAutocomplete: yup
      .string()
      .when(['manuallySetAddress'], (vals, schema) => {
        const [manuallySetAddress] = vals as [boolean]
        if (!manuallySetAddress) {
          return schema.required(
            'Veuillez sélectionner une adresse parmi les suggestions'
          )
        }
        return schema
      }),
    street: yup.string().when('isOpenToPublic', {
      is: 'true',
      then: (schema) =>
        schema.trim().required('Veuillez renseigner une adresse postale'),
      otherwise: (schema) => schema.nullable(),
    }),
    postalCode: yup.string().when('isOpenToPublic', {
      is: 'true',
      then: (schema) =>
        schema
          .required('Veuillez renseigner un code postal')
          .min(5, 'Veuillez renseigner un code postal valide')
          .max(5, 'Veuillez renseigner un code postal valide'),
      otherwise: (schema) => schema.nullable(),
    }),
    city: yup.string().when('isOpenToPublic', {
      is: 'true',
      then: (schema) => schema.trim().required('Veuillez renseigner une ville'),
      otherwise: (schema) => schema.nullable(),
    }),
    coords: yup
      .string()
      .trim()
      .when(['manuallySetAddress'], (vals, schema) => {
        const [manuallySetAddress] = vals as [boolean]
        if (manuallySetAddress) {
          return schema
            .required('Veuillez renseigner les coordonnées GPS')
            .test('coords', 'Veuillez respecter le format attendu', (value) =>
              checkCoords(value)
            )
        }
        return schema
      }),
    bookingEmail: yup.string().test(emailSchema),
    isOpenToPublic: yup.string(),
    name: yup
      .string()
      .required(`Veuillez renseigner la raison sociale de votre lieu`),
  })
  .concat(SiretOrCommentValidationSchema)
