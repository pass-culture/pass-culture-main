import * as yup from 'yup'

import { checkCoords } from 'utils/coords'

export const validationSchema = {
  locationLabel: yup.string(),

  addressAutocomplete: yup
    .string()
    .when(['isVenueVirtual', 'manuallySetAddress'], {
      is: false,
      then: (schema) =>
        schema.required(
          'Veuillez sélectionner une adresse parmi les suggestions'
        ),
    }),

  street: yup.string().when('isVenueVirtual', {
    is: false,
    then: (schema) =>
      schema.required('Veuillez renseigner une adresse postale'),
  }),
  postalCode: yup.string().when('isVenueVirtual', {
    is: false,
    then: (schema) => schema.required('Veuillez renseigner un code postal'),
  }),
  city: yup.string().when('isVenueVirtual', {
    is: false,
    then: (schema) => schema.required('Veuillez renseigner une ville'),
  }),
  coords: yup.string().when(['isVenueVirtual', 'manuallySetAddress'], {
    is: (isVenueVirtual: boolean, manuallySetAddress: boolean) =>
      !isVenueVirtual && manuallySetAddress,
    then: (schema) =>
      schema
        .required('Veuillez renseigner les coordonnées GPS')
        .test('coords', 'Veuillez respecter le format attendu', (value) =>
          checkCoords(value)
        ),
  }),
}
