import type {
  CreatePriceCategoryModel,
  EditPriceCategoryModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  PriceCategoryResponseModel,
  ThingStockCreateBodyModel,
  ThingStockUpdateBodyModel,
} from '@/apiClient/v1'
import type { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'

type UpdatabledPriceTableEntryFormValues = Partial<
  CreatePriceCategoryModel &
    EditPriceCategoryModel &
    ThingStockCreateBodyModel &
    ThingStockUpdateBodyModel
>

type ReadonlyPriceTableEntryFormValues = Readonly<
  Partial<
    Omit<
      PriceCategoryResponseModel & GetOfferStockResponseModel,
      keyof UpdatabledPriceTableEntryFormValues
    >
  >
>

export type PriceTableEntryApiValues = UpdatabledPriceTableEntryFormValues &
  ReadonlyPriceTableEntryFormValues

export interface PriceTableFormContext {
  isCaledonian: boolean
  mode: OFFER_WIZARD_MODE
  offer: GetIndividualOfferWithAddressResponseModel
}
