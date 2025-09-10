import { WithdrawalTypeEnum } from '@/apiClient/v1'
import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import type { IndividualOfferPracticalInfosFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const defaultFormValues: IndividualOfferPracticalInfosFormValues = {
    withdrawalType: null,
    bookingContact: null,
    bookingEmail: null,
    externalTicketOfficeUrl: null,
    withdrawalDetails: null,
    withdrawalDelay: null,
    receiveNotificationEmails: false,
  }

  const cases: {
    description: string
    formValues: Partial<IndividualOfferPracticalInfosFormValues>
    expectedErrors: string[]
    canBeWithdrawable?: boolean
  }[] = [
    {
      description: 'valid for default form values',
      formValues: defaultFormValues,
      expectedErrors: [],
    },
    {
      description: 'invalid for missing withdrawal informations',
      formValues: defaultFormValues,
      expectedErrors: [
        'Veuillez sélectionner une méthode de distribution',
        'Veuillez renseigner une adresse email',
      ],
      canBeWithdrawable: true,
    },
    {
      description: 'invalid for missing withdrawal delay',
      formValues: {
        ...defaultFormValues,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        bookingContact: 'test@test.co',
      },
      expectedErrors: [
        'Vous devez choisir l’une des options de délai de retrait',
      ],
      canBeWithdrawable: true,
    },
    {
      description: 'invalid for a pass culture withdrawal email',
      formValues: {
        ...defaultFormValues,
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: '10',
        bookingContact: 'test@passculture.app',
      },
      expectedErrors: ['Ce mail doit vous appartenir'],
      canBeWithdrawable: true,
    },
    {
      description: 'invalid for a missing notification email',
      formValues: {
        ...defaultFormValues,
        receiveNotificationEmails: true,
      },
      expectedErrors: ['Veuillez renseigner une adresse email'],
    },
  ]

  cases.forEach(
    ({ description, formValues, expectedErrors, canBeWithdrawable }) => {
      it(`should validate the form for case: ${description}`, async () => {
        const errors = await getYupValidationSchemaErrors(
          getValidationSchema(canBeWithdrawable),
          formValues
        )
        expect(errors).toEqual(expectedErrors)
      })
    }
  )
})
