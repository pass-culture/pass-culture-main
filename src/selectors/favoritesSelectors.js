import {createSelector} from "reselect";
import get from "lodash.get";


export const filterValidFavorites = favorite => {
  const offerId = get(favorite, 'offerId')
  console.log("OfferId: " + offerId)
  if (!offerId) return false
}

export const selectFavorites = createSelector(
  state => state.data.favorites,
  allFavorites => allFavorites
)

export const selectMyFavorites = createSelector(
  state => state.data.favorites,
  allFavorites => {
    console.log("allFavorites: " + allFavorites)
    const filtered = allFavorites.filter(filterValidFavorites)
    console.log("filtered: " + filtered)
    return filtered
  }
)

export default selectMyFavorites
