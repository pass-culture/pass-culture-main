import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'
import { emailSchema } from 'commons/utils/isValidEmail'

import { validationSchema as locationSchema } from '../components/OfferLocation/validationSchema'

import { UsefulInformationFormValues } from './types'

const isAnyTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

export const getValidationSchema = ({
  subcategories,
  isDigitalOffer = false,
}: {
  subcategories: string[]
  isDigitalOffer?: boolean
}) => {
  const validationSchema = {
    accessibility: yup
      .object<AccessibilityFormValues>()
      .test({
        name: 'is-any-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isAnyTrue,
      })
      .shape({
        mental: yup.boolean().required(),
        audio: yup.boolean().required(),
        visual: yup.boolean().required(),
        motor: yup.boolean().required(),
        none: yup.boolean().required(),
      })
      .required(),
    addressAutocomplete: yup.string(),
    banId: yup.string(),
    bookingContact: yup.string().when([], {
      is: () => subcategories.includes('bookingContact'),
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema)
          .test({
            name: 'organisationEmailNotPassCulture',
            message: 'Ce mail doit vous appartenir',
            test: (value) => !value.toLowerCase().endsWith('@passculture.app'),
          }),
    }),
    bookingEmail: yup.string().when('receiveNotificationEmails', {
      is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema),
    }),
    city: yup.string(),
    coords: yup.string(),
    externalTicketOfficeUrl: yup
      .string()
      .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
    inseeCode: yup.string(),
    isEvent: yup.boolean(),
    isNational: yup.boolean(),
    latitude: yup.string(),
    locationLabel: yup.string(),
    longitude: yup.string(),
    manuallySetAddress: yup.boolean(),
    offerLocation: yup.string(),
    postalCode: yup.string(),
    receiveNotificationEmails: yup.boolean(),
    'search-addressAutocomplete': yup.string(),
    street: yup.string(),
    withdrawalDelay: yup.string().when('withdrawalType', {
      is: (withdrawalType: WithdrawalTypeEnum) =>
        subcategories.includes('withdrawalDelay') &&
        [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
          withdrawalType
        ),
      then: (schema) =>
        schema.required('Vous devez choisir l’une des options ci-dessus'),
    }),
    withdrawalType: yup.string<WithdrawalTypeEnum>().when([], {
      is: () => subcategories.includes('withdrawalType'),
      then: (schema) =>
        schema
          .oneOf(Object.values(WithdrawalTypeEnum))
          .required('Veuillez sélectionner l’une de ces options'),
    }),
    withDrawalDetails: yup.string(),
  }

  const res = yup.object<UsefulInformationFormValues>().shape({
    ...validationSchema,
    ...(!isDigitalOffer ? locationSchema : {}),
  })

  return res
}
