import type {
  CreatePriceCategoryModel,
  EditPriceCategoryModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export type PriceTableEntryModel = Partial<
  CreatePriceCategoryModel & EditPriceCategoryModel & GetOfferStockResponseModel
>

export interface PriceTableFormContext {
  isCaledonian: boolean
  mode: OFFER_WIZARD_MODE
  offer: GetIndividualOfferWithAddressResponseModel
}
