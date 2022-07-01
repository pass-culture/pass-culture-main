import * as yup from 'yup'

import { OfferAddressType } from 'apiClient/v1'
import { parsePhoneNumberFromString } from 'libphonenumber-js'

const isOneTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

const isPhoneValid = (phone: string | undefined): boolean => {
  if (!phone) {
    return false
  }

  const phoneNumber = parsePhoneNumberFromString(phone, 'FR')
  const isValid = phoneNumber?.isValid()
  return Boolean(isValid)
}

const returnFalse = (): boolean => false
const returnTrue = (): boolean => true

export const validationSchema = yup.object().shape({
  category: yup.string().required('Veuillez sélectionner une catégorie'),
  subCategory: yup
    .string()
    .required('Veuillez sélectionner une sous-catégorie'),
  title: yup.string().max(90).required('Veuillez renseigner un titre'),
  description: yup.string().max(1000),
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
      then: yup.string().required('Veuillez renseigner une adresse'),
    }),
    venueId: yup.string().when('addressType', {
      is: OfferAddressType.OFFERER_VENUE,
      then: yup.string().required('Veuillez sélectionner un lieu'),
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
    .required('Veuillez renseigner un numéro de téléphone')
    .test({
      name: 'is-phone-valid',
      message: 'Le numéro de téléphone n’est pas valide',
      test: isPhoneValid,
    }),
  email: yup
    .string()
    .required('Veuillez renseigner une adresse e-mail')
    .email(
      'L’e-mail renseigné n’est pas valide. Exemple : votrenom@votremail.com'
    ),
  notifications: yup.boolean(),
  notificationEmail: yup.string().when('notifications', {
    is: true,
    then: yup
      .string()
      .required('Veuillez renseigner une adresse e-mail')
      .email(
        'L’e-mail renseigné n’est pas valide. Exemple : votrenom@votremail.com'
      ),
  }),
})

export const validationSchemaWithDomains = validationSchema.concat(
  yup.object().shape({
    domains: yup.array().test({
      message: 'Veuillez renseigner un domaine',
      test: domains => Boolean(domains?.length && domains.length > 0),
    }),
    'search-domains': yup.string().when('domains', (domains, schema) =>
      schema.test({
        name: 'search-domains-invalid',
        message: 'error',
        test: domains.length === 0 ? returnFalse : returnTrue,
      })
    ),
  })
)
