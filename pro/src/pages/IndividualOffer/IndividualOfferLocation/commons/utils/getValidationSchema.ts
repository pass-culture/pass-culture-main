import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'
import { offerFormUrlRegex } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'

import { OFFER_LOCATION } from '../../../commons/constants'
import type { LocationFormValues, PhysicalAddressSubformValues } from '../types'

export const PhysicalLocationValidationSchema = yup
  .object<PhysicalAddressSubformValues>()
  .shape({
    addressAutocomplete: nonEmptyStringOrNull().when(
      ['offerLocation', 'isManualEdition'],
      {
        is: (offerLocation: string, isManualEdition: boolean) =>
          offerLocation === OFFER_LOCATION.OTHER_ADDRESS && !isManualEdition,
        then: (schema) =>
          schema.required(
            'Veuillez sélectionner une adresse parmi les suggestions'
          ),
      }
    ),
    banId: nonEmptyStringOrNull(),
    city: yup
      .string()
      .trim()
      .defined()
      .transform((value: string | null) =>
        typeof value === 'string' ? removeQuotes(value) : value
      )
      .when(['offerLocation'], {
        is: (offerLocation: string) =>
          offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
        then: (schema) => schema.required('Veuillez renseigner une ville'),
      }),
    coords: nonEmptyStringOrNull().when(['isManualEdition'], {
      is: (isManualEdition: boolean) => isManualEdition,
      then: (schema) =>
        schema
          .required('Veuillez renseigner les coordonnées GPS')
          .test('coords', 'Veuillez respecter le format attendu', (value) =>
            checkCoords(value)
          ),
    }),
    inseeCode: nonEmptyStringOrNull(),
    isManualEdition: yup.boolean().defined(),
    isVenueLocation: yup
      .boolean()
      .when('offerLocation', {
        is: (offerLocation: string) =>
          offerLocation !== OFFER_LOCATION.OTHER_ADDRESS,
        then: (schema) => schema.transform(() => true),
        otherwise: (schema) => schema.transform(() => false),
      })
      .defined(),
    label: nonEmptyStringOrNull(),
    latitude: yup.string().trim().defined(),
    longitude: yup.string().trim().defined(),
    offerLocation: yup
      .string()
      .default(OFFER_LOCATION.OTHER_ADDRESS)
      .defined()
      .required('Veuillez sélectionner un choix'),
    postalCode: yup
      .string()
      .trim()
      .defined()
      .when(['offerLocation'], {
        is: (offerLocation: string) =>
          offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
        then: (schema) => schema.required('Veuillez renseigner un code postal'),
      })
      .min(5, 'Veuillez renseigner un code postal valide')
      .max(5, 'Veuillez renseigner un code postal valide'),
    'search-addressAutocomplete': nonEmptyStringOrNull(),
    street: yup
      .string()
      .trim()
      .defined()
      .transform((value: string | null) =>
        typeof value === 'string' ? removeQuotes(value) : value
      )
      .when(['offerLocation'], {
        is: (offerLocation: string) =>
          offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
        then: (schema) =>
          schema.required('Veuillez renseigner une adresse postale'),
      }),
  })

export const getValidationSchema = ({ isDigital }: { isDigital: boolean }) => {
  return yup.object<LocationFormValues>().shape({
    location: yup
      .mixed<PhysicalAddressSubformValues>()
      .nullable()
      .defined()
      .when({
        is: () => isDigital,
        then: () => yup.mixed().nullable().defined(),
        otherwise: () => PhysicalLocationValidationSchema.defined(),
      }),
    url: nonEmptyStringOrNull().when({
      is: () => isDigital,
      then: (schema) =>
        schema
          .nonNullable(
            'Veuillez renseigner une URL valide. Ex : https://exemple.com'
          )
          .matches(offerFormUrlRegex, {
            message:
              'Veuillez renseigner une URL valide. Ex : https://exemple.com',
            excludeEmptyString: true,
          }),
    }),
  })
}
