import { addYears, isBefore } from 'date-fns'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { OfferAddressType } from 'apiClient/v1'
import { MAX_DETAILS_LENGTH } from 'core/OfferEducational'
import { toDateStrippedOfTimezone } from 'utils/date'

const threeYearsFromNow = addYears(new Date(), 3)

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return true
  }

  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}

const isNotEmpty = (description: string | undefined): boolean =>
  description ? Boolean(description.trim().length > 0) : false

export function getOfferEducationalValidationSchema(isFormatActive: boolean) {
  return yup.object().shape({
    category: isFormatActive
      ? yup.string()
      : yup.string().required('Veuillez sélectionner une catégorie'),
    subCategory: isFormatActive
      ? yup.string()
      : yup.string().required('Veuillez sélectionner une sous-catégorie'),
    title: yup.string().max(110).required('Veuillez renseigner un titre'),
    description: yup
      .string()
      .test({
        name: 'is-not-empty',
        message: 'Veuillez renseigner une description',
        test: isNotEmpty,
      })
      .max(MAX_DETAILS_LENGTH),
    duration: yup
      .string()
      .matches(
        /[0-9]{1,2}:[0-5][0-9]/,
        'Veuillez renseigner une durée en heures au format hh:mm. Exemple: 1:30'
      ),
    offererId: yup.string().required('Veuillez sélectionner une structure'),
    venueId: yup.string().required('Veuillez sélectionner un lieu'),
    eventAddress: yup.object().shape({
      addressType: yup
        .string()
        .oneOf([
          OfferAddressType.OFFERER_VENUE,
          OfferAddressType.OTHER,
          OfferAddressType.SCHOOL,
        ]),
      otherAddress: yup.string().when('addressType', {
        is: OfferAddressType.OTHER,
        then: (schema) => schema.required('Veuillez renseigner une adresse'),
      }),
      venueId: yup
        .number()
        .nullable()
        .when('addressType', {
          is: OfferAddressType.OFFERER_VENUE,
          then: (schema) => schema.required('Veuillez sélectionner un lieu'),
        }),
    }),
    participants: yup.object().test({
      name: 'is-one-true',
      message: 'Veuillez sélectionner au moins un niveau scolaire',
      test: isOneTrue,
    }),
    accessibility: yup
      .object()
      .test({
        name: 'is-one-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isOneTrue,
      })
      .shape({
        mental: yup.boolean(),
        audio: yup.boolean(),
        visual: yup.boolean(),
        motor: yup.boolean(),
        none: yup.boolean(),
      }),
    phone: yup.string().test({
      name: 'is-phone-valid',
      message:
        'Veuillez entrer un numéro de téléphone valide, exemple : 612345678',
      test: isPhoneValid,
    }),
    email: yup
      .string()
      .required('Veuillez renseigner une adresse email')
      .email('Veuillez renseigner un email valide, exemple : mail@exemple.com'),
    notificationEmails: yup
      .array()
      .of(
        yup
          .string()
          .email(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )
          .required('Veuillez renseigner une adresse email')
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
    formats: isFormatActive
      ? yup.array().test({
          message: 'Veuillez renseigner un format',
          test: (format) => Boolean(format?.length && format.length > 0),
        })
      : yup.array(),
    'search-formats': isFormatActive
      ? yup.string().when('formats', (format, schema) =>
          schema.test({
            name: 'search-formats-invalid',
            message: 'error',
            test: () => format.length > 0,
          })
        )
      : yup.string(),
    interventionArea: yup.array().when('eventAddress', {
      is: (eventAddress: { addressType: OfferAddressType }) =>
        eventAddress.addressType !== OfferAddressType.OFFERER_VENUE,
      then: (schema) =>
        schema.min(1, 'Veuillez renseigner une zone de mobilité'),
    }),
    'search-interventionArea': yup
      .string()
      .when(['interventionArea', 'eventAddress'], {
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
    priceDetail: yup.string().max(MAX_DETAILS_LENGTH),
    beginningDate: yup.string().when('isTemplate', {
      is: true,
      then: (schema) =>
        schema.required('Veuillez renseigner une date de début'),
    }),
    endingDate: yup.string().when('isTemplate', {
      is: true,
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
  })
}
