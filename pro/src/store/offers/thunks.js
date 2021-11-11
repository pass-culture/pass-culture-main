import * as pcapi from 'repository/pcapi/pcapi'

import { setCategories } from './actions'

export const loadCategories = () => {
  return async dispatch => {
    return pcapi.loadCategories().then(({ categories, subcategories }) => {
      dispatch(
        setCategories({
          categories,
          subCategories: subcategories,
        })
      )
    })
  }
}
