import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { emailSchema } from '@/commons/utils/isValidEmail'

import { SiretOrCommentValidationSchema } from '../components/SiretOrCommentFields/validationSchema'

export const venueSettingsValidationSchema = yup
  .object()
  .shape({
    manuallySetAddress: yup.boolean().required().default(false),
    'search-addressAutocomplete': yup.string().defined().nullable(),
    addressAutocomplete: yup
      .string()
      .defined()
      .when(['$isVenueVirtual', 'manuallySetAddress'], (vals, schema) => {
        const [isVenueVirtual, manuallySetAddress] = vals as [boolean, boolean]
        if (!isVenueVirtual && !manuallySetAddress) {
          return schema.required(
            'Veuillez sélectionner une adresse parmi les suggestions'
          )
        }
        return schema
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
    inseeCode: yup.string().defined().nullable(),
    city: yup.string().trim().required('Veuillez renseigner une ville'),
    latitude: yup.string().defined().nullable(),
    longitude: yup.string().defined().nullable(),
    banId: yup.string().defined().nullable(),
    venueSiret: yup.mixed<number | string>().defined(),
    coords: yup
      .string()
      .defined()
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
    bookingEmail: yup
      .string()
      .required('Veuillez renseigner une adresse email')
      .test(emailSchema),
    name: yup
      .string()
      .required(`Veuillez renseigner la raison sociale de votre lieu`),
    publicName: yup.string().defined().nullable(),
    withdrawalDetails: yup.string().default(''),
    venueType: yup
      .string()
      .defined()
      .when('$isVenueActivityFeatureActive', {
        is: true,
        then: (schema) =>
          schema.required('Veuillez sélectionner une activité principale'),
      }),
  })
  .concat(SiretOrCommentValidationSchema)

export type VenueSettingsFormValuesType = yup.InferType<
  typeof venueSettingsValidationSchema
>

export const getVenueSettingsValidationSchema = ({
  isVenueActivityFeatureActive,
}: {
  isVenueActivityFeatureActive: boolean
}) => {
  return yup
    .object()
    .shape({
      manuallySetAddress: yup.boolean().nullable(),
      addressAutocomplete: yup
        .string()
        .when(['$isVenueVirtual', 'manuallySetAddress'], (vals, schema) => {
          const [isVenueVirtual, manuallySetAddress] = vals as [
            boolean,
            boolean,
          ]
          if (!isVenueVirtual && !manuallySetAddress) {
            return schema.required(
              'Veuillez sélectionner une adresse parmi les suggestions'
            )
          }
          return schema
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
      name: yup
        .string()
        .required(`Veuillez renseigner la raison sociale de votre lieu`),
      ...(isVenueActivityFeatureActive
        ? {
            venueType: yup
              .string()
              .required('Veuillez sélectionner une activité principale'),
          }
        : {}),
    })
    .concat(SiretOrCommentValidationSchema)
}
