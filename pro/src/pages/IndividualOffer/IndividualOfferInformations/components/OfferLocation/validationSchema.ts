import { checkCoords } from 'commons/utils/coords'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import * as yup from 'yup'

// TODO (igabriele, 2025-07-24): Move that into IndividualOffer/IndividualOfferInformations/commons/validationSchema.ts.
// + Add typings.
export const validationSchema = {
  addressAutocomplete: yup
    .string()
    .trim()
    .when(['offerLocation', 'manuallySetAddress'], {
      is: (offerLocation: string, manuallySetAddress: boolean) =>
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS && !manuallySetAddress,
      then: (schema) =>
        schema.required(
          'Veuillez sélectionner une adresse parmi les suggestions'
        ),
    }),
  city: yup
    .string()
    .trim()
    .when(['offerLocation'], {
      is: (offerLocation: string) =>
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
      then: (schema) => schema.required('Veuillez renseigner une ville'),
    }),
  coords: yup
    .string()
    .trim()
    .when(['offerLocation', 'manuallySetAddress'], {
      is: (offerLocation: string, manuallySetAddress: boolean) =>
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS && manuallySetAddress,
      then: (schema) =>
        schema
          .required('Veuillez renseigner les coordonnées GPS')
          .test('coords', 'Veuillez respecter le format attendu', (value) =>
            checkCoords(value)
          ),
    }),
  locationLabel: yup.string(),
  offerLocation: yup.string().trim().required('Veuillez sélectionner un choix'),
  postalCode: yup
    .string()
    .trim()
    .when(['offerLocation'], {
      is: (offerLocation: string) =>
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
      then: (schema) => schema.required('Veuillez renseigner un code postal'),
    })
    .min(5, 'Veuillez renseigner un code postal valide')
    .max(5, 'Veuillez renseigner un code postal valide'),
  street: yup
    .string()
    .trim()
    .when(['offerLocation'], {
      is: (offerLocation: string) =>
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
      then: (schema) =>
        schema.required('Veuillez renseigner une adresse postale'),
    }),
}
