import type { PriceCategoriesFormValues, PriceCategoryForm } from './types'

const hasFieldChange = (
  priceCategories: PriceCategoryForm[],
  initialPriceCategories: Record<string, Partial<PriceCategoryForm>>,
  field: keyof PriceCategoryForm
) =>
  priceCategories.some((priceCategory) => {
    // if no id, it is new and has no stocks
    if (!priceCategory.id) {
      return false
    }
    // have fields which trigger warning been edited ?
    const initialpriceCategory = initialPriceCategories[priceCategory.id]
    return initialpriceCategory[field] !== priceCategory[field]
  })

/**
 * @function arePriceCategoriesChanged
 * Returns `true` if at least one of the initial price categories has changed
 * and `false` otherwise (even if there are additional price cateogires in the values).
 * */
export const arePriceCategoriesChanged = (
  initialValues: PriceCategoriesFormValues,
  values: PriceCategoriesFormValues
): boolean => {
  const initialPriceCategories: Record<
    string,
    Partial<PriceCategoryForm>
  > = initialValues.priceCategories.reduce(
    (dict: Record<string, Partial<PriceCategoryForm>>, priceCategory) => {
      dict[priceCategory.id || 'new'] = {
        id: priceCategory.id,
        label: priceCategory.label,
        price: priceCategory.price,
      }
      return dict
    },
    {}
  )

  const changedPriceCategories = values.priceCategories.filter(
    (priceCategory) => {
      if (!priceCategory.id) {
        return false
      }
      if (
        priceCategory.price !==
          initialPriceCategories[priceCategory.id].price ||
        priceCategory.label !== initialPriceCategories[priceCategory.id].label
      ) {
        return true
      }
      return false
    }
  )

  return hasFieldChange(changedPriceCategories, initialPriceCategories, 'price')
}
