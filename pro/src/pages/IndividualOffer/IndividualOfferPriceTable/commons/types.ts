import type {
  CreatePriceCategoryModel,
  EditPriceCategoryModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  ThingStockCreateBodyModel,
  ThingStockUpdateBodyModel,
} from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

export type PriceTableEntryModel = Partial<
  CreatePriceCategoryModel &
    EditPriceCategoryModel &
    ThingStockCreateBodyModel &
    ThingStockUpdateBodyModel &
    GetOfferStockResponseModel
>

export interface PriceTableFormContext {
  isCaledonian: boolean
  mode: OFFER_WIZARD_MODE
  offer: GetIndividualOfferWithAddressResponseModel
}
