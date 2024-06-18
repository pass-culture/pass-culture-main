import { addYears, isBefore } from 'date-fns'
import { parsePhoneNumberFromString } from 'libphonenumber-js'
import * as yup from 'yup'

import { OfferAddressType } from 'apiClient/v1'
import { MAX_DETAILS_LENGTH } from 'core/OfferEducational/constants'
import {
  OfferEducationalFormValues,
  OfferDatesType,
} from 'core/OfferEducational/types'
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

export function getOfferEducationalValidationSchema() {
  return yup.object().shape({
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
    email: yup
      .string()
      .when(['contactOptions', 'isTemplate'], {
        is: (
          contactOptions: OfferEducationalFormValues['contactOptions'],
          isTemplate: boolean
        ) => !isTemplate || contactOptions?.email,
        then: (schema) =>
          schema.required('Veuillez renseigner une adresse email'),
      })
      .email(
        'Veuillez renseigner une adresse email valide, exemple : mail@exemple.com'
      ),
    contactUrl: yup.string().when(['contactOptions', 'contactFormType'], {
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
    contactOptions: yup.object().when('isTemplate', {
      is: (isTemplate: boolean) => isTemplate,
      then: (schema) =>
        schema.required().test({
          name: 'is-one-true',
          message: 'Veuillez sélectionner au moins un moyen de contact',
          test: isOneTrue,
        }),
    }),
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
    formats: yup.array().test({
      message: 'Veuillez renseigner un format',
      test: (format) => Boolean(format?.length && format.length > 0),
    }),
    'search-formats': yup.string().when('formats', (format, schema) =>
      schema.test({
        name: 'search-formats-invalid',
        message: 'error',
        test: () => format.length > 0,
      })
    ),
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
  })
}
