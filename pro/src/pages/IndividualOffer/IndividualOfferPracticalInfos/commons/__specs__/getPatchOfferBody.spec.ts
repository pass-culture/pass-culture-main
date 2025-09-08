import { WithdrawalTypeEnum } from '@/apiClient/v1'

import { getPatchOfferBody } from '../getPatchOfferBody'
import type { IndividualOfferPracticalInfosFormValues } from '../types'

const defaultFormValues: IndividualOfferPracticalInfosFormValues = {
  bookingAllowedMode: 'later',
  bookingAllowedDate: '2050-12-12',
  bookingAllowedTime: '12:12',
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
    expect(getPatchOfferBody(defaultFormValues, '56', false)).toEqual(
      expect.objectContaining({
        bookingAllowedDatetime: expect.stringContaining('T'),
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
        '56',
        false
      )
    ).toEqual(
      expect.objectContaining({
        withdrawalDelay: null,
      })
    )
  })
})
