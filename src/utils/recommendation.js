export function setUniqIdOnRecommendation(recommendation) {
  const { mediation, offer } = recommendation
  const { productId } = offer || {}
  const { tutoIndex } = mediation || {}

  let uniqId
  if (productId) {
    uniqId = `product_${productId}`
  } else if (typeof tutoIndex !== 'undefined') {
    uniqId = `tuto_${tutoIndex}`
  }
  return Object.assign({ uniqId }, recommendation)
}

export default setUniqIdOnRecommendation
