import { OfferStatus } from 'apiClient/v1'

export type GetCollectiveOfferTemplateSuccessPayload = {
  id: string
  isActive: boolean
  status: OfferStatus
  isBooked: boolean
  isCancellable: boolean
  venueDepartmentCode: string
  managingOffererId: string
  isEducational: boolean
  isShowcase: boolean
  offerId?: string | null
  educationalPriceDetails?: string | null
}
