import * as yup from 'yup'

import { OFFER_LOCATION } from 'components/IndividualOfferForm/OfferLocation/constants'
import { checkCoords } from 'utils/coords'

const locationSchema = {
  addressAutocomplete: yup
    .string()
    .when(['offerlocation', 'manuallySetAddress'], {
      is: (offerLocation: string, manuallySetAddress: boolean) =>
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS && !manuallySetAddress,
      then: (schema) =>
        schema.required(
          'Veuillez sélectionner une adresse parmi les suggestions'
        ),
    }),
  street: yup.string().when('offerlocation', {
    is: OFFER_LOCATION.OTHER_ADDRESS,
    then: (schema) =>
      schema.required('Veuillez renseigner une adresse postale'),
  }),
  postalCode: yup.string().when('offerlocation', {
    is: OFFER_LOCATION.OTHER_ADDRESS,
    then: (schema) => schema.required('Veuillez renseigner un code postal'),
  }),
  city: yup.string().when('offerlocation', {
    is: OFFER_LOCATION.OTHER_ADDRESS,
    then: (schema) => schema.required('Veuillez renseigner une ville'),
  }),
  coords: yup.string().when(['offerlocation', 'manuallySetAddress'], {
    is: (offerLocation: string, manuallySetAddress: boolean) =>
      offerLocation === OFFER_LOCATION.OTHER_ADDRESS && manuallySetAddress,
    then: (schema) =>
      schema
        .required('Veuillez renseigner les coordonnées GPS')
        .test('coords', 'Veuillez respecter le format attendu', (value) =>
          checkCoords(value)
        ),
  }),
}

export const validationSchema = {
  locationLabel: yup.string(),
  ...locationSchema,
}
