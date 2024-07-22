import {
  CollectiveBookingStatus,
  CollectiveOfferStatus,
  CollectiveOffersStockResponseModel,
} from 'apiClient/v1'
import {
  collectiveOfferFactory,
  getCollectiveOfferFactory,
} from 'utils/collectiveApiFactories'

import {
  canArchiveCollectiveOffer,
  canArchiveCollectiveOfferFromSummary,
} from '../canArchiveCollectiveOffer'

describe('canArchiveCollectiveOffer', () => {
  const stocks: Array<CollectiveOffersStockResponseModel> = [
    {
      beginningDatetime: String(new Date()),
      hasBookingLimitDatetimePassed: false,
      remainingQuantity: 1,
    },
  ]

  const offerStatus = [
    CollectiveOfferStatus.ACTIVE,
    CollectiveOfferStatus.REJECTED,
    CollectiveOfferStatus.INACTIVE,
  ]

  it.each(offerStatus)(
    'should return true when collective offer status is %s',
    (status) => {
      expect(
        canArchiveCollectiveOffer(
          collectiveOfferFactory({
            status,
            stocks,
          })
        )
      ).toStrictEqual(true)
    }
  )

  it.each(offerStatus)(
    'should return true when collective offer status is %s in summary page',
    (status) => {
      expect(
        canArchiveCollectiveOfferFromSummary(
          getCollectiveOfferFactory({
            status,
          })
        )
      ).toStrictEqual(true)
    }
  )

  it('should return true when collective offer status is "EXPIRED" and booking status "CANCELLED"', () => {
    expect(
      canArchiveCollectiveOffer(
        collectiveOfferFactory({
          status: CollectiveOfferStatus.EXPIRED,
          stocks,
          booking: { booking_status: CollectiveBookingStatus.CANCELLED, id: 1 },
        })
      )
    ).toStrictEqual(true)
  })

  it('should return false when collective offer with status "EXPIRED" and booking status "PENDING"', () => {
    expect(
      canArchiveCollectiveOffer(
        collectiveOfferFactory({
          status: CollectiveOfferStatus.EXPIRED,
          stocks,
          booking: { booking_status: CollectiveBookingStatus.PENDING, id: 1 },
        })
      )
    ).toStrictEqual(false)
  })

  it('should return false when collective offer status is "SOLD_OUT"', () => {
    expect(
      canArchiveCollectiveOffer(
        collectiveOfferFactory({
          status: CollectiveOfferStatus.SOLD_OUT,
          stocks,
        })
      )
    ).toStrictEqual(false)
  })

  it('should return true when collective offer with status "PENDING" and booking status "REIMBURSED"', () => {
    expect(
      canArchiveCollectiveOffer(
        collectiveOfferFactory({
          status: CollectiveOfferStatus.PENDING,
          stocks,
          booking: {
            booking_status: CollectiveBookingStatus.REIMBURSED,
            id: 1,
          },
        })
      )
    ).toStrictEqual(true)
  })

  it('should return true when collective offer with status "PENDING" and booking status "USED" and after beginningDatetime + 48h ', () => {
    expect(
      canArchiveCollectiveOffer(
        collectiveOfferFactory({
          status: CollectiveOfferStatus.PENDING,
          stocks: [
            {
              ...stocks[0]!,
              beginningDatetime: String(new Date('2020-01-01')),
            },
          ],
          booking: {
            booking_status: CollectiveBookingStatus.USED,
            id: 1,
          },
        })
      )
    ).toStrictEqual(true)
  })

  it('should return false when collective offer with status "PENDING" and booking status "USED" and before beginningDatetime + 48h ', () => {
    expect(
      canArchiveCollectiveOffer(
        collectiveOfferFactory({
          status: CollectiveOfferStatus.PENDING,
          stocks: [{ ...stocks[0]!, beginningDatetime: String(new Date()) }],
          booking: {
            booking_status: CollectiveBookingStatus.USED,
            id: 1,
          },
        })
      )
    ).toStrictEqual(false)
  })
})
