import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { emailSchema } from '@/commons/utils/isValidEmail'

import { SiretOrCommentValidationSchema } from '../components/SiretOrCommentFields/validationSchema'

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
