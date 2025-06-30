import { addYears, isBefore } from 'date-fns'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import {
    CollectiveLocationType,
    OfferAddressType,
    StudentLevels,
} from 'apiClient/v1'
import {
    MAX_DESCRIPTION_LENGTH,
    MAX_PRICE_DETAILS_LENGTH,
} from 'commons/core/OfferEducational/constants'
import {
    OfferDatesType,
    OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import { checkCoords } from 'commons/utils/coords'
import { toDateStrippedOfTimezone } from 'commons/utils/date'
import { emailSchema } from 'commons/utils/isValidEmail'
import { extractPhoneParts } from 'ui-kit/form/PhoneNumberInput/PhoneNumberInput'

const threeYearsFromNow = addYears(new Date(), 3)

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone || !extractPhoneParts(phone).phoneNumber) {
    return true
  }

  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}

const isNotEmpty = (description: string | undefined): boolean =>
  description ? Boolean(description.trim().length > 0) : false

export function getOfferEducationalValidationSchema(
  isCollectiveOaActive: boolean
) {
  return yup.object<OfferEducationalFormValues>().shape({
    title: yup.string().max(110).required('Veuillez renseigner un titre'),
    description: yup
      .string()
      .required('Veuillez renseigner une description')
      .test({
        name: 'is-not-empty',
        message: 'Veuillez renseigner une description',
        test: isNotEmpty,
      })
      .max(MAX_DESCRIPTION_LENGTH),
    duration: yup
      .string()
      .matches(
        /^$|([0-9]{1,2}:[0-5][0-9])/,
        'Veuillez entrer une durée sous la forme HH:MM (ex: 1:30 pour 1h30)'
      ),
    offererId: yup
      .string()
      .required('Veuillez sélectionner une entité juridique'),
    venueId: yup.string().required('Veuillez sélectionner une structure'),
    location: isCollectiveOaActive
      ? yup.object().shape({
          locationType: yup
            .string()
            .oneOf([
              CollectiveLocationType.ADDRESS,
              CollectiveLocationType.SCHOOL,
              CollectiveLocationType.TO_BE_DEFINED,
            ]),
        })
      : yup.mixed(),
    addressAutocomplete: isCollectiveOaActive
      ? yup
          .string()
          .trim()
          .when(
            [
              'location.locationType',
              'location.address.id_oa',
              'location.address.isManualEdition',
            ],
            {
              is: (
                locationType: string,
                id_oa: string,
                isManualEdition: boolean
              ) =>
                locationType === CollectiveLocationType.ADDRESS &&
                id_oa === 'SPECIFIC_ADDRESS' &&
                !isManualEdition,
              then: (schema) =>
                schema.required(
                  'Veuillez sélectionner une adresse parmi les suggestions'
                ),
            }
          )
      : yup.mixed(),
    eventAddress: isCollectiveOaActive
      ? yup.mixed().required()
      : yup
          .object()
          .required()
          .shape({
            addressType: yup.string<OfferAddressType>().required(),
            otherAddress: yup.string().when('addressType', {
              is: OfferAddressType.OTHER,
              then: (schema) =>
                schema.required('Veuillez renseigner une adresse'),
            }),
            venueId: yup
              .number()
              .nullable()
              .when('addressType', {
                is: OfferAddressType.OFFERER_VENUE,
                then: (schema) =>
                  schema.required('Veuillez sélectionner un lieu'),
              }),
          }),
    participants: yup.object<{ [key in StudentLevels]: boolean }>().test({
      name: 'is-one-true',
      message: 'Veuillez sélectionner au moins un niveau scolaire',
      test: isOneTrue,
    }),
    accessibility: yup
      .object()
      .required('Veuillez sélectionner au moins un critère d’accessibilité')
      .test({
        name: 'is-one-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isOneTrue,
      })
      .shape({
        mental: yup.boolean().required(),
        audio: yup.boolean().required(),
        visual: yup.boolean().required(),
        motor: yup.boolean().required(),
        none: yup.boolean().required(),
      }),
    phone: yup
      .string()
      .when(['contactOptions', 'isTemplate'], {
        is: (
          contactOptions: OfferEducationalFormValues['contactOptions'],
          isTemplate: boolean
        ) => isTemplate && contactOptions?.phone,
        then: (schema) =>
          schema.required('Veuillez renseigner un numéro de téléphone'),
      })
      .test({
        name: 'is-phone-valid',
        message:
          'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
        test: isPhoneValid,
      }),
    email: yup.string().when(['contactOptions', 'isTemplate'], {
      is: (
        contactOptions: OfferEducationalFormValues['contactOptions'],
        isTemplate: boolean
      ) => !isTemplate || contactOptions?.email,
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema),
    }),
    contactUrl: yup
      .string()
      .nullable()
      .when(['contactOptions', 'contactFormType'], {
        is: (
          contactOptions: OfferEducationalFormValues['contactOptions'],
          contactFormType: OfferEducationalFormValues['contactFormType']
        ) => contactOptions?.form && contactFormType === 'url',
        then: (schema) =>
          schema
            .required('Veuillez renseigner une URL de contact')
            .url(
              'Veuillez renseigner une URL valide, exemple : https://mon-formulaire.fr'
            ),
      }),
    contactFormType: yup.string<'form' | 'url'>(),
    imageUrl: yup.string(),
    imageCredit: yup.string(),
    nationalProgramId: yup.string(),
    isTemplate: yup.boolean().required(),
    datesType: yup.string<OfferDatesType>(),
    hour: yup.string(),
    contactOptions: yup
      .object()
      .notRequired()
      .nonNullable()
      .shape({
        email: yup.boolean().required(),
        phone: yup.boolean().required(),
        form: yup.boolean().required(),
      })
      .when('isTemplate', {
        is: (isTemplate: boolean) => isTemplate,
        then: (schema) =>
          schema.required().test({
            name: 'is-one-true',
            message: 'Veuillez sélectionner au moins un moyen de contact',
            test: isOneTrue,
          }),
      }),
    notificationEmails: yup.array().of(
      yup.object().shape({
        email: yup
          .string()
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema),
      })
    ),
    domains: yup.array().test({
      message: 'Veuillez renseigner un domaine',
      test: (domains) => Boolean(domains?.length && domains.length > 0),
    }),
    'search-domains': yup.string().when('domains', (domains, schema) =>
      schema.test({
        name: 'search-domains-invalid',
        message: 'error',
        test: () => domains.length > 0,
      })
    ),
    formats: yup
      .array()
      .required()
      .test({
        message: 'Veuillez renseigner un format',
        test: (format) => format.length > 0,
      }),
    'search-formats': yup.string().when('formats', (format, schema) =>
      schema.test({
        name: 'search-formats-invalid',
        message: 'error',
        test: () => format.length > 0,
      })
    ),
    interventionArea: isCollectiveOaActive
      ? yup.array().when('location.locationType', {
          is: (locationType: CollectiveLocationType) =>
            locationType !== CollectiveLocationType.ADDRESS,
          then: (schema) =>
            schema.min(1, 'Veuillez renseigner au moins un département'),
        })
      : yup.array().when('eventAddress', {
          is: (eventAddress: { addressType: OfferAddressType }) =>
            eventAddress.addressType !== OfferAddressType.OFFERER_VENUE,
          then: (schema) =>
            schema.min(1, 'Veuillez renseigner une zone de mobilité'),
        }),
    'search-interventionArea': isCollectiveOaActive
      ? yup.mixed()
      : yup.string().when(['interventionArea', 'eventAddress'], {
          is: (
            interventionArea: string[],
            eventAddress: { addressType: OfferAddressType }
          ) => {
            return (
              eventAddress.addressType !== OfferAddressType.OFFERER_VENUE &&
              interventionArea.length === 0
            )
          },
          then: (schema) => schema.required(),
        }),
    priceDetail: yup.string().max(MAX_PRICE_DETAILS_LENGTH),
    beginningDate: yup.string().when(['isTemplate', 'datesType'], {
      is: (isTemplate: boolean, datesType: OfferDatesType) =>
        isTemplate && datesType === 'specific_dates',
      then: (schema) =>
        schema.required('Veuillez renseigner une date de début'),
    }),
    endingDate: yup.string().when(['isTemplate', 'datesType'], {
      is: (isTemplate: boolean, datesType: OfferDatesType) =>
        isTemplate && datesType === 'specific_dates',
      then: (schema) =>
        schema
          .required('Veuillez renseigner une date de fin')
          .test(
            'endDateNoTooFar',
            'La date de fin que vous avez choisie est trop éloignée',
            (endDate) => {
              return isBefore(
                toDateStrippedOfTimezone(endDate),
                threeYearsFromNow
              )
            }
          ),
    }),
    'search-addressAutocomplete': yup.string(),
    street: yup
      .string()
      .nullable()
      .trim()
      .when(['location.locationType', 'location.address.isManualEdition'], {
        is: (locationType: string, isManualEdition: boolean) =>
          locationType === CollectiveLocationType.ADDRESS && isManualEdition,
        then: (schema) =>
          schema.required('Veuillez renseigner une adresse postale'),
      }),
    postalCode: yup
      .string()
      .trim()
      .when(['location.locationType', 'location.address.isManualEdition'], {
        is: (locationType: string, isManualEdition: boolean) =>
          locationType === CollectiveLocationType.ADDRESS && isManualEdition,
        then: (schema) =>
          schema
            .required('Veuillez renseigner un code postal')
            .min(5, 'Veuillez renseigner un code postal valide')
            .max(5, 'Veuillez renseigner un code postal valide'),
        otherwise: (schema) => schema.notRequired(),
      }),
    city: yup
      .string()
      .trim()
      .when(['location.locationType', 'location.address.isManualEdition'], {
        is: (locationType: string, isManualEdition: boolean) =>
          locationType === CollectiveLocationType.ADDRESS && isManualEdition,
        then: (schema) => schema.required('Veuillez renseigner une ville'),
      }),
    coords: yup
      .string()
      .trim()
      .when(['location.locationType', 'location.address.isManualEdition'], {
        is: (locationType: string, isManualEdition: boolean) =>
          locationType === CollectiveLocationType.ADDRESS && isManualEdition,
        then: (schema) =>
          schema
            .required('Veuillez renseigner les coordonnées GPS')
            .test('coords', 'Veuillez respecter le format attendu', (value) =>
              checkCoords(value)
            ),
      }),
    banId: yup.string().nullable(),
    inseeCode: yup.string().nullable(),
    latitude: yup.string(),
    longitude: yup.string(),
  })
}
