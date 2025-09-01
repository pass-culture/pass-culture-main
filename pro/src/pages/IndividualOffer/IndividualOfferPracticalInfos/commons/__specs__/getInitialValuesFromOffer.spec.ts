import { WithdrawalTypeEnum } from '@/apiClient/v1'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { MOCKED_SUBCATEGORY } from '@/pages/IndividualOffer/commons/__mocks__/constants'

import { getInitialValuesFromOffer } from '../getInitialValuesFromOffer'

describe('getInitialValuesFromOffer', () => {
  const offer = getIndividualOfferFactory({
    bookingAllowedDatetime: '2070-03-23T15:08:33Z',
    bookingContact: 'bookingContact@example.co',
    bookingEmail: 'bookingEmail@example.co',
    externalTicketOfficeUrl: 'http://url.co',
    withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
    withdrawalDelay: 10,
    withdrawalDetails: 'Withdrawal details',
  })

  it('should get the default values from an offer with a withdrawable sub category', () => {
    const withdrawableSubCategory = MOCKED_SUBCATEGORY.WIDTHDRAWABLE

    expect(getInitialValuesFromOffer(offer, withdrawableSubCategory)).toEqual(
      expect.objectContaining({
        bookingAllowedMode: 'later',
        bookingContact: 'bookingContact@example.co',
        bookingEmail: 'bookingEmail@example.co',
        externalTicketOfficeUrl: 'http://url.co',
        withdrawalType: 'by_email',
        withdrawalDelay: '10',
        receiveNotificationEmails: true,
        withdrawalDetails: 'Withdrawal details',
      })
    )
  })

  it('should get the default values from an offer with a non withdrawable sub category', () => {
    const nonWithdrawableSubCategory = subcategoryFactory({
      canBeWithdrawable: false,
    })

    expect(
      getInitialValuesFromOffer(
        {
          ...offer,
          bookingEmail: undefined,
          bookingAllowedDatetime: undefined,
          withdrawalType: null,
        },
        nonWithdrawableSubCategory
      )
    ).toEqual(
      expect.objectContaining({
        bookingAllowedMode: 'now',
        withdrawalType: null,
        receiveNotificationEmails: false,
      })
    )
  })
})
