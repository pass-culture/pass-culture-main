import { OfferStatus } from 'api/v1/gen'
import { GetStockOfferSuccessPayload } from 'core/OfferEducational'

export const offerFactory = (
  offerExtend: Partial<GetStockOfferSuccessPayload>
): GetStockOfferSuccessPayload => ({
  id: 'OFFER_ID',
  isActive: true,
  status: OfferStatus.PENDING,
  isBooked: false,
  venueDepartmentCode: '75',
  managingOffererId: 'OFFERER_ID',
  isEducational: true,
  isShowcase: false,
  ...offerExtend,
})
