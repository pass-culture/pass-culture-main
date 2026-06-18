import { WithdrawalTypeEnum } from '@/apiClient/v1'

import { getPatchOfferBody } from '../getPatchOfferBody'
import type { IndividualOfferPracticalInfosFormValues } from '../types'

const defaultFormValues: IndividualOfferPracticalInfosFormValues = {
  bookingContact: 'bookingContact@example.co',
  receiveNotificationEmails: true,
  bookingEmail: 'bookingEmail@example.co',
  externalTicketOfficeUrl: 'http://url.co',
  withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
  withdrawalDelay: '10',
  withdrawalDetails: 'Withdrawal details',
}

describe('getPatchOfferBody', () => {
  it('should create the patch body from the form values', () => {
    expect(getPatchOfferBody(defaultFormValues, false)).toEqual(
      expect.objectContaining({
        bookingContact: 'bookingContact@example.co',
        bookingEmail: 'bookingEmail@example.co',
        externalTicketOfficeUrl: 'http://url.co',
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: 10,
        withdrawalDetails: 'Withdrawal details',
      })
    )
  })

  it('should not send the withdrawal delay if the withdrawal type is NO_TICKET', () => {
    expect(
      getPatchOfferBody(
        {
          ...defaultFormValues,
          withdrawalDelay: '10',
          withdrawalType: WithdrawalTypeEnum.NO_TICKET,
        },
        false
      )
    ).toEqual(
      expect.objectContaining({
        withdrawalDelay: null,
      })
    )
  })
})
