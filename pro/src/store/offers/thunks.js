import { api } from 'apiClient/api'

import { setCategories } from './actions'

export const loadCategories = () => {
  return async dispatch => {
    return api.getCategories().then(({ categories, subcategories }) => {
      dispatch(
        setCategories({
          categories,
          subCategories: subcategories,
        })
      )
    })
  }
}
