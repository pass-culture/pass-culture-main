import createCachedSelector from 're-reselect'

export const getProductById = createCachedSelector(
  state => state.data.products,
  (state, productId) => productId,
  (products, productId) => products.find(product => product.id === productId)
)((state, productId) => productId)
