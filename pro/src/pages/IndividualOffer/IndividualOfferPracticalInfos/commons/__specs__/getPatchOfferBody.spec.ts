import { WithdrawalTypeEnum } from '@/apiClient/v1'

import { getPatchOfferBody } from '../getPatchOfferBody'
import type { IndividualOfferPracticalInfosFormValues } from '../types'

describe('getPatchOfferBody', () => {
  it('should create the patch body from the form values', () => {
    const formValues: IndividualOfferPracticalInfosFormValues = {
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

    expect(getPatchOfferBody(formValues, '56', false)).toEqual(
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
})
