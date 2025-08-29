import * as yup from 'yup'

import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { emailSchema } from '@/commons/utils/isValidEmail'
import {
  bookingAllowedDateValidationSchema,
  bookingAllowedTimeValidationSchema,
} from '@/pages/IndividualOfferSummary/IndividualOfferSummary/components/EventPublicationForm/validationSchema'

import type { IndividualOfferPracticalInfosFormValues } from './types'

export function getValidationSchema(canBeWithdrawable?: boolean) {
  return yup.object<IndividualOfferPracticalInfosFormValues>().shape({
    bookingAllowedMode: yup.string<'now' | 'later'>().required(),
    bookingAllowedDate: yup.string().when('bookingAllowedMode', {
      is: 'later',
      then: (schema) => bookingAllowedDateValidationSchema(schema),
    }),
    bookingAllowedTime: yup.string().when('bookingAllowedMode', {
      is: 'later',
      then: (schema) => bookingAllowedTimeValidationSchema(schema),
    }),
    withdrawalType: yup.string<WithdrawalTypeEnum>().when([], {
      is: () => canBeWithdrawable,
      then: (schema) =>
        schema
          .oneOf(Object.values(WithdrawalTypeEnum))
          .required('Veuillez sélectionner une méthode de distribution'),
    }),
    withdrawalDelay: yup.string().when('withdrawalType', {
      is: (type: WithdrawalTypeEnum) =>
        [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
          type
        ),
      then: (schema) =>
        schema.required(
          'Vous devez choisir l’une des options de délai de retrait'
        ),
    }),
    withdrawalDetails: yup.string(),
    bookingContact: yup.string().when([], {
      is: () => canBeWithdrawable,
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
    externalTicketOfficeUrl: yup
      .string()
      .url('Veuillez renseigner une URL valide. Ex : https://exemple.com'),
    receiveNotificationEmails: yup.boolean(),
    bookingEmail: yup.string().when('receiveNotificationEmails', {
      is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
      then: (schema) =>
        schema
          .required('Veuillez renseigner une adresse email')
          .test(emailSchema),
    }),
  })
}
