import type {
  PriceCategoriesFormValues,
  PriceCategoryForm,
} from '@/pages/IndividualOffer/IndividualOfferPriceCategories/commons/types'

let priceCategoryFormId = 1
export const priceCategoryFormFactory = (
  customPriceCategory: Partial<PriceCategoryForm> = {}
): PriceCategoryForm => ({
  label: `Tarif ${priceCategoryFormId++}`,
  price: 20,
  ...customPriceCategory,
})

export const priceCategoriesFormValuesFactory = (
  customPriceCategoriesFormValues: Partial<PriceCategoriesFormValues> = {}
): PriceCategoriesFormValues => ({
  priceCategories: [priceCategoryFormFactory()],
  isDuo: false,
  ...customPriceCategoriesFormValues,
})
