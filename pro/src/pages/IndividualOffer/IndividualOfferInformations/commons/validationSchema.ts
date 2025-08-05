import { WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'
import { emailSchema } from 'commons/utils/isValidEmail'
import { offerFormUrlRegex } from 'pages/IndividualOffer/IndividualOfferDetails/commons/validationSchema'
import * as yup from 'yup'

import { validationSchema as locationSchema } from '../components/OfferLocation/validationSchema'

import { UsefulInformationFormValues } from './types'

const isAnyTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

export const getValidationSchema = ({
  conditionalFields,
  isNewOfferCreationFlowFeatureActive,
  isOfferOnline,
}: {
  conditionalFields: string[]
  isNewOfferCreationFlowFeatureActive: boolean
  isOfferOnline: boolean
}) => {
  const accessibility = yup.lazy(() =>
    isNewOfferCreationFlowFeatureActive
      ? yup
          .mixed<any>() // `any` represents `undefined` here which is impossible to type via yup
          .optional()
      : yup
          .object<AccessibilityFormValues>()
          .test({
            name: 'is-any-true',
            message:
              'Veuillez sélectionner au moins un critère d’accessibilité',
            test: isAnyTrue,
          })
          .shape({
            mental: yup.boolean().required(),
            audio: yup.boolean().required(),
            visual: yup.boolean().required(),
            motor: yup.boolean().required(),
            none: yup.boolean().required(),
          })
          .required()
  )

  const url = yup.lazy(() =>
    isNewOfferCreationFlowFeatureActive
      ? yup.string().when('subcategoryId', {
          is: () => isOfferOnline,
          then: (schema) =>
            schema
              .matches(offerFormUrlRegex, {
                message:
                  'Veuillez renseigner une URL valide. Ex : https://exemple.com',
                excludeEmptyString: true,
              })
              .required(
                'Veuillez renseigner une URL valide. Ex : https://exemple.com'
              ),
          otherwise: (schema) => schema.nullable(),
        })
      : yup
          .mixed<any>() // `any` represents `undefined` here which is impossible to type via yup
          .optional()
  )

  const maybeLocationSchema = isOfferOnline ? {} : { ...locationSchema }

  return yup.object<UsefulInformationFormValues>().shape({
    accessibility,
    addressAutocomplete: yup.string(),
    banId: yup.string(),
    bookingContact: yup.string().when([], {
      is: () => conditionalFields.includes('bookingContact'),
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
    url,
    withdrawalDelay: yup.string().when('withdrawalType', {
      is: (withdrawalType: WithdrawalTypeEnum) =>
        conditionalFields.includes('withdrawalDelay') &&
        [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
          withdrawalType
        ),
      then: (schema) =>
        schema.required('Vous devez choisir l’une des options ci-dessus'),
    }),
    withdrawalType: yup.string<WithdrawalTypeEnum>().when([], {
      is: () => conditionalFields.includes('withdrawalType'),
      then: (schema) =>
        schema
          .oneOf(Object.values(WithdrawalTypeEnum))
          .required('Veuillez sélectionner l’une de ces options'),
    }),
    withDrawalDetails: yup.string(),
    ...maybeLocationSchema,
  })
}
