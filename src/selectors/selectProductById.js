import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, productId) {
  return productId || ''
}

export const selectProductById = createCachedSelector(
  state => state.data.products,
  (state, productId) => productId,
  (products, productId) =>
    (products || []).find(product => product.id === productId)
)(mapArgsToCacheKey)

export default selectProductById
