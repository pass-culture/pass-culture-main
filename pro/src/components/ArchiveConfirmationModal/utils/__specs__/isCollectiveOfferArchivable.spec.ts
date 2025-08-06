import {
  CollectiveOfferAllowedAction,
  CollectiveOffersStockResponseModel,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import { collectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'

import { isCollectiveOfferArchivable } from '../isCollectiveOfferArchivable'

describe('isCollectiveOfferArchivable', () => {
  const stocks: Array<CollectiveOffersStockResponseModel> = [
    {
      startDatetime: String(new Date()),
      hasBookingLimitDatetimePassed: false,
      remainingQuantity: 1,
    },
  ]

  it('should return true when collective offer is archivable', () => {
    expect(
      isCollectiveOfferArchivable(
        collectiveOfferFactory({
          stocks,
          allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
        })
      )
    ).toStrictEqual(true)
  })

  it('should return true when collective template offer is archivable', () => {
    expect(
      isCollectiveOfferArchivable(
        collectiveOfferFactory({
          isShowcase: true,
          allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
        })
      )
    ).toStrictEqual(true)
  })

  it('should return false when collective offer is not archivable', () => {
    expect(
      isCollectiveOfferArchivable(
        collectiveOfferFactory({
          stocks,
          allowedActions: [],
        })
      )
    ).toStrictEqual(false)
  })

  it('should return false when collective template offer is not archivable', () => {
    expect(
      isCollectiveOfferArchivable(
        collectiveOfferFactory({
          isShowcase: true,
          allowedActions: [],
        })
      )
    ).toStrictEqual(false)
  })
})
