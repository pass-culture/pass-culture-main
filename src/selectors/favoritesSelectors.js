import {createSelector} from "reselect";

export const selectMyFavorites = createSelector(
  state => state.data.favorites,
  favorites => {
    return favorites
  }
)

export default selectMyFavorites
