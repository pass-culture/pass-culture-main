import * as yup from 'yup'

import { checkCoords } from '@/commons/utils/coords'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'
import { offerFormUrlRegex } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'

import { OFFER_LOCATION } from '../../../commons/constants'
import type { LocationFormValues } from '../types'

export const getValidationSchema = ({
  isOfferSubcategoryOnline,
}: {
  isOfferSubcategoryOnline: boolean
}) => {
  return yup.object<LocationFormValues>().shape({
    addressAutocomplete: nonEmptyStringOrNull().when(
      ['offerLocation', 'isManualEdition'],
      {
        is: (offerLocation: string, isManualEdition: boolean) =>
          !isOfferSubcategoryOnline &&
          offerLocation === OFFER_LOCATION.OTHER_ADDRESS &&
          !isManualEdition,
        then: (schema) =>
          schema.nonNullable(
            'Veuillez sélectionner une adresse parmi les suggestions'
          ),
      }
    ),
    banId: nonEmptyStringOrNull(),
    city: nonEmptyStringOrNull().when(['offerLocation'], {
      is: (offerLocation: string) =>
        !isOfferSubcategoryOnline &&
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
      then: (schema) => schema.nonNullable('Veuillez renseigner une ville'),
    }),
    coords: nonEmptyStringOrNull().when(['offerLocation', 'isManualEdition'], {
      is: (offerLocation: string, isManualEdition: boolean) =>
        !isOfferSubcategoryOnline &&
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS &&
        isManualEdition,
      then: (schema) =>
        schema
          .nonNullable('Veuillez renseigner les coordonnées GPS')
          .test('coords', 'Veuillez respecter le format attendu', (value) =>
            checkCoords(value)
          ),
    }),
    inseeCode: nonEmptyStringOrNull(),
    isManualEdition: yup.boolean().defined(),
    latitude: nonEmptyStringOrNull(),
    locationLabel: nonEmptyStringOrNull(),
    longitude: nonEmptyStringOrNull(),
    offerLocation: nonEmptyStringOrNull().when({
      is: () => !isOfferSubcategoryOnline,
      then: (schema) => schema.nonNullable('Veuillez sélectionner un choix'),
    }),
    postalCode: nonEmptyStringOrNull()
      .when(['offerLocation'], {
        is: (offerLocation: string) =>
          !isOfferSubcategoryOnline &&
          offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
        then: (schema) =>
          schema.nonNullable('Veuillez renseigner un code postal'),
      })
      .min(5, 'Veuillez renseigner un code postal valide')
      .max(5, 'Veuillez renseigner un code postal valide'),
    'search-addressAutocomplete': nonEmptyStringOrNull(),
    street: nonEmptyStringOrNull().when(['offerLocation'], {
      is: (offerLocation: string) =>
        !isOfferSubcategoryOnline &&
        offerLocation === OFFER_LOCATION.OTHER_ADDRESS,
      then: (schema) =>
        schema.nonNullable('Veuillez renseigner une adresse postale'),
    }),
    url: nonEmptyStringOrNull().when({
      is: () => isOfferSubcategoryOnline,
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
