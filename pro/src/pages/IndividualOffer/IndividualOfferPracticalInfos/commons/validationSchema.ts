import * as yup from 'yup'

import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { emailSchema } from '@/commons/utils/isValidEmail'
import { nonEmptyStringOrNull } from '@/commons/utils/yup/nonEmptyStringOrNull'
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
    withdrawalType: nonEmptyStringOrNull()
      .oneOf(Object.values(WithdrawalTypeEnum))
      .when([], {
        is: () => canBeWithdrawable,
        then: (schema) =>
          schema.nonNullable(
            'Veuillez sélectionner une méthode de distribution'
          ),
      }),
    withdrawalDelay: nonEmptyStringOrNull().when('withdrawalType', {
      is: (type: WithdrawalTypeEnum) =>
        [WithdrawalTypeEnum.BY_EMAIL, WithdrawalTypeEnum.ON_SITE].includes(
          type
        ),
      then: (schema) =>
        schema.nonNullable(
          'Vous devez choisir l’une des options de délai de retrait'
        ),
    }),
    withdrawalDetails: nonEmptyStringOrNull(),
    bookingContact: nonEmptyStringOrNull().when([], {
      is: () => canBeWithdrawable,
      then: (schema) =>
        schema
          .nonNullable('Veuillez renseigner une adresse email')
          .test(emailSchema)
          .test({
            name: 'organisationEmailNotPassCulture',
            message: 'Ce mail doit vous appartenir',
            test: (value) => !value.toLowerCase().endsWith('@passculture.app'),
          }),
    }),
    externalTicketOfficeUrl: nonEmptyStringOrNull().url(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    ),
    receiveNotificationEmails: yup.boolean().required(),
    bookingEmail: nonEmptyStringOrNull().when('receiveNotificationEmails', {
      is: (receiveNotificationEmails: boolean) => receiveNotificationEmails,
      then: (schema) =>
        schema
          .nonNullable('Veuillez renseigner une adresse email')
          .test(emailSchema),
    }),
  })
}
