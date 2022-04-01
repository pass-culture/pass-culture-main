import { createCachedSelector } from 'store/utils'

export const selectProductById = createCachedSelector(
  state => state.data.products,
  (state, productId) => productId,
  (products = [], productId) =>
    products.find(product => product.id === productId)
)((state, productId = '') => productId)
