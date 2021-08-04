import { createSelector } from 'reselect'

const selectCategoriesAndSubcategories = state => state.data.categories

export const selectSubcategory = createSelector(
  selectCategoriesAndSubcategories,
  (state, offer) => offer.subcategoryId,
  (categories, subcategoryId) => {
    const { subcategories } = categories[0]
    const subcategory = subcategories.find(subcategory => subcategory.id === subcategoryId)
    return subcategory
  }
)
