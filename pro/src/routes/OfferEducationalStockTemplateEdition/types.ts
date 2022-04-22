import { OfferStatus } from 'api/v1/gen'

export type GetCollectiveOfferTemplateSuccessPayload = {
  id: string
  isActive: boolean
  status: OfferStatus
  isBooked: boolean
  venueDepartmentCode: string
  managingOffererId: string
  isEducational: boolean
  isShowcase: boolean
  offerId?: string | null
  educationalPriceDetails?: string | null
}
