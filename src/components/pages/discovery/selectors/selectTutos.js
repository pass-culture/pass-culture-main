const isTuto = recommendation => {
  const identifier = recommendation.productOrTutoIdentifier

  return identifier === 'tuto_0' || identifier === 'tuto_1'
}

const selectTutos = state => state.data.recommendations.filter(isTuto)

export default selectTutos
