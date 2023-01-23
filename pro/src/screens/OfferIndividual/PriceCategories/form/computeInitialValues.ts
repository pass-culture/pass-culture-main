import { PriceCategoriesFormValues } from './types'

export const computeInitialValues = (): PriceCategoriesFormValues => {
  return {
    priceCategories: [
      {
        label: '',
        price: '',
      },
    ],
    isDuo: true,
  }
}
