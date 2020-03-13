const isTutorial = recommendation => {
  const identifier = recommendation.productOrTutoIdentifier
  return identifier === 'tuto_0' || identifier === 'tuto_1'
}

const selectTutorials = state => state.data.recommendations.filter(isTutorial)

export default selectTutorials
