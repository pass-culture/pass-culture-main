import * as yup from 'yup'

import { OFFER_LOCATION } from 'components/IndividualOfferForm/OfferLocation/constants'
import { checkCoords } from 'utils/coords'

const locationSchema = {
  offerlocation: yup.string().when('isVenueVirtual', {
    is: false,
    then: (schema) => schema.required('Veuillez sélectionner un choix'),
  }),
  addressAutocomplete: yup
    .string()
    .when(['offerlocation', 'manuallySetAddress', 'isVenueVirtual'], {
      is: (
        offerLocation: string,
        manuallySetAddress: boolean,
        isVenueVirtual: boolean
      ) =>
        !isVenueVirtual &&
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS &&
        !manuallySetAddress,
      then: (schema) =>
        schema.required(
          'Veuillez sélectionner une adresse parmi les suggestions'
        ),
    }),
  street: yup.string().when(['offerlocation', 'isVenueVirtual'], {
    is: (offerLocation: string, isVenueVirtual: boolean) =>
      !isVenueVirtual && offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
    then: (schema) =>
      schema.required('Veuillez renseigner une adresse postale'),
  }),
  postalCode: yup.string().when(['offerlocation', 'isVenueVirtual'], {
    is: (offerLocation: string, isVenueVirtual: boolean) =>
      !isVenueVirtual && offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
    then: (schema) => schema.required('Veuillez renseigner un code postal'),
  }),
  city: yup.string().when(['offerlocation', 'isVenueVirtual'], {
    is: (offerLocation: string, isVenueVirtual: boolean) =>
      !isVenueVirtual && offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
    then: (schema) => schema.required('Veuillez renseigner une ville'),
  }),
  coords: yup
    .string()
    .when(['offerlocation', 'manuallySetAddress', 'isVenueVirtual'], {
      is: (
        offerLocation: string,
        manuallySetAddress: boolean,
        isVenueVirtual: boolean
      ) =>
        !isVenueVirtual &&
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS &&
        manuallySetAddress,
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
