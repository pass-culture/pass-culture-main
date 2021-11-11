import { createSelector } from 'reselect'

export const selectSubcategoriesAndSearchGroups = state => state.data.categories

export const selectSubcategory = createSelector(
  selectSubcategoriesAndSearchGroups,
  (state, offer) => offer.subcategoryId,
  (categories, subcategoryId) => {
    const { subcategories } = categories[0]
    const subcategory = subcategories.find(subcategory => subcategory.id === subcategoryId)
    return subcategory
  }
)

export const selectSearchGroup = createSelector(
  selectSubcategoriesAndSearchGroups,
  (state, offer) => offer.subcategoryId,
  (categories, subcategoryId) => {
    if (!subcategoryId) return {}
    const { subcategories, searchGroups } = categories[0]
    const subcategory = subcategories.find(subcategory => subcategory.id === subcategoryId)
    const searchGroup = searchGroups.find(
      searchGroup => searchGroup.name === subcategory.searchGroupName
    )
    return searchGroup
  }
)

export const selectSearchGroupBySearchResult = createSelector(
  selectSubcategoriesAndSearchGroups,
  (state, offerFromResult) => offerFromResult.searchGroupName,
  (categories, searchGroupName) => {
    if (!searchGroupName) return {}
    const { searchGroups } = categories[0]
    return searchGroups.find(searchGroup => searchGroup.name === searchGroupName)
  }
)
