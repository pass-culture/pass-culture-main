import { createSelector } from 'reselect'

export const getProductById = createSelector(
  state => state.data.products,
  (state, productId) => productId,
  (products, productId) => products.find(product => product.id === productId)
)
