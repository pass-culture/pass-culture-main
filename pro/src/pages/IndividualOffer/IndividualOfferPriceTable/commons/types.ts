import type {
  CreatePriceCategoryModel,
  EditPriceCategoryModel,
  GetIndividualOfferResponseModelV2,
  GetOfferStockResponseModel,
} from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export type PriceTableEntryModel = Partial<
  CreatePriceCategoryModel & EditPriceCategoryModel & GetOfferStockResponseModel
>

export interface PriceTableFormContext {
  isCaledonian: boolean | undefined
  mode: OFFER_WIZARD_MODE
  offer: GetIndividualOfferResponseModelV2
}
