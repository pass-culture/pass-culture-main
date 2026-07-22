import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  UpsertPriceCategoryModel,
} from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export type PriceTableEntryModel = Partial<
  UpsertPriceCategoryModel & GetOfferStockResponseModel
>

export interface PriceTableFormContext {
  isCaledonian: boolean | undefined
  mode: OFFER_WIZARD_MODE
  offer: GetIndividualOfferWithAddressResponseModel
}
