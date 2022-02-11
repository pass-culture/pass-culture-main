import { GetStockOfferSuccessPayload } from 'core/OfferEducational'
import { OfferStatus } from 'custom_types/offer'

export const offerFactory = (
  offerExtend: Partial<GetStockOfferSuccessPayload>
): GetStockOfferSuccessPayload => ({
  id: 'OFFER_ID',
  isActive: true,
  status: OfferStatus.OFFER_STATUS_PENDING,
  isBooked: false,
  venueDepartmentCode: '75',
  managingOffererId: 'OFFERER_ID',
  isEducational: true,
  isShowcase: false,
  ...offerExtend,
})
