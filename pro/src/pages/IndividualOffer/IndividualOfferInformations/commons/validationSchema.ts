import * as yup from 'yup'

import { WithdrawalTypeEnum } from 'apiClient/v1'
import { emailSchema } from 'commons/utils/isValidEmail'

import { validationSchema as locationSchema } from '../components/OfferLocation/validationSchema'

import { UsefulInformationFormValues } from './types'

const isAnyTrue = (values: Record<string, boolean>): boolean =>
  Object.values(values).includes(true)

type ValidationSchemaProps = {
  subcategories: string[]
  isDigitalOffer?: boolean
}

export const getValidationSchema = ({
  subcategories,
  isDigitalOffer = false,
}: ValidationSchemaProps) => {
  const validationSchema = {
    withdrawalType: yup.string().when([], {
      is: () => subcategories.includes('withdrawalType'),
      then: (schema) =>
        schema
          .oneOf(Object.values(WithdrawalTypeEnum))
          .required('Veuillez sélectionner l’une de ces options'),
    }),
    withdrawalDelay: yup.string().when('withdrawalType', {
      is: (withdrawalType: WithdrawalTypeEnum) =>
        subcategories.includes('withdrawalDelay') &&
        [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
          withdrawalType
        ),
      then: (schema) =>
        schema.required('Vous devez choisir l’une des options ci-dessus'),
    }),
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
    accessibility: yup
      .object()
      .test({
        name: 'is-any-true',
        message: 'Veuillez sélectionner au moins un critère d’accessibilité',
        test: isAnyTrue,
      })
      .shape({
        mental: yup.boolean(),
        audio: yup.boolean(),
        visual: yup.boolean(),
        motor: yup.boolean(),
        none: yup.boolean(),
      }),
    bookingEmail: yup.string().when('receiveNotificationEmails', {
      is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema),
    }),
    externalTicketOfficeUrl: yup
      .string()
      .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
  }

  return yup.object<UsefulInformationFormValues>().shape({
    ...validationSchema,
    ...(!isDigitalOffer ? locationSchema : {}),
  })
}
