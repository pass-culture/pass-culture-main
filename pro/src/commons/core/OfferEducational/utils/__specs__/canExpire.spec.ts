import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { defaultCollectiveOffer } from '@/commons/utils/factories/adageFactories'

import { canExpire } from '../canExpire'

describe('canExpire', () => {
  it.each([
    [CollectiveOfferDisplayedStatus.PREBOOKED],
    [CollectiveOfferDisplayedStatus.PUBLISHED],
  ])('should return true for status %s', (displayedStatus) => {
    expect(
      canExpire({ ...defaultCollectiveOffer, displayedStatus })
    ).toBeTruthy()
  })

  it.each([
    [CollectiveOfferDisplayedStatus.ARCHIVED],
    [CollectiveOfferDisplayedStatus.BOOKED],
    [CollectiveOfferDisplayedStatus.CANCELLED],
    [CollectiveOfferDisplayedStatus.DRAFT],
    [CollectiveOfferDisplayedStatus.ENDED],
    [CollectiveOfferDisplayedStatus.EXPIRED],
    [CollectiveOfferDisplayedStatus.HIDDEN],
    [CollectiveOfferDisplayedStatus.REIMBURSED],
    [CollectiveOfferDisplayedStatus.REJECTED],
    [CollectiveOfferDisplayedStatus.UNDER_REVIEW],
  ])('should return true for status %s', (displayedStatus) => {
    expect(
      canExpire({ ...defaultCollectiveOffer, displayedStatus })
    ).toBeFalsy()
  })
})
