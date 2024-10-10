import * as yup from 'yup'

import { checkCoords } from 'utils/coords'

export const getValidationSchema = (isVenueVirtual: boolean) =>
  yup.object().shape({
    addressAutocomplete: yup
      .string()
      .when(['isVenueVirtual', 'manuallySetAddress'], {
        is: (isVenueVirtual: string, manuallySetAddress: boolean) =>
          !isVenueVirtual && !manuallySetAddress,
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
      .min(4, 'Veuillez renseigner un code postal valide'),

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

    bookingEmail: isVenueVirtual
      ? yup.string()
      : yup
          .string()
          .email(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )
          .required('Veuillez renseigner une adresse email'),
    name: yup
      .string()
      .required(`Veuillez renseigner la raison sociale de votre lieu`),
    venueType: yup
      .string()
      .required('Veuillez sélectionner une activité principale'),
  })
