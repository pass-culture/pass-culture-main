import { GetStockOfferSuccessPayload } from 'core/OfferEducational'
import { OfferStatus } from 'apiClient/v1'

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
