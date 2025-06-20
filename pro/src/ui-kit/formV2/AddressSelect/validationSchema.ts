import * as yup from 'yup'

import { checkCoords } from 'commons/utils/coords'

export const validationSchema = {
  addressAutocomplete: yup.string().when(['manuallySetAddress'], {
    is: (manuallySetAddress: boolean) => !manuallySetAddress,
    then: (schema) =>
      schema.required(
        'Veuillez sélectionner une adresse parmi les suggestions'
      ),
  }),
  street: yup
    .string()
    .trim()
    .required('Veuillez renseigner une adresse postale'),
  postalCode: yup
    .string()
    .trim()
    .required('Veuillez renseigner un code postal')
    .min(5, 'Veuillez renseigner un code postal valide')
    .max(5, 'Veuillez renseigner un code postal valide'),

  city: yup.string().trim().required('Veuillez renseigner une ville'),
  coords: yup
    .string()
    .trim()
    .when(['manuallySetAddress'], {
      is: (manuallySetAddress: boolean) => manuallySetAddress,
      then: (schema) =>
        schema
          .required('Veuillez renseigner les coordonnées GPS')
          .test('coords', 'Veuillez respecter le format attendu', (value) =>
            checkCoords(value)
          ),
    }),
}