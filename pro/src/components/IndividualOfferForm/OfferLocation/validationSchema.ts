import * as yup from 'yup'

import { checkCoords } from 'utils/coords'

export const validationSchema = {
  locationLabel: yup.string(),

  addressAutocomplete: yup.string().when('manuallySetAddress', {
    is: false,
    then: (schema) =>
      schema.required(
        'Veuillez sélectionner une adresse parmi les suggestions'
      ),
  }),

  street: yup.string().required('Veuillez renseigner une adresse postale'),
  postalCode: yup.string().required('Veuillez renseigner un code postal'),
  city: yup.string().required('Veuillez renseigner une ville'),
  coords: yup.string().when('manuallySetAddress', {
    is: true,
    then: (schema) =>
      schema
        .required('Veuillez renseigner les coordonnées GPS')
        .test('coords', 'Veuillez respecter le format attendu', (value) =>
          checkCoords(value)
        ),
  }),
}
