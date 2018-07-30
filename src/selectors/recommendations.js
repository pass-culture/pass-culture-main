import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.recommendations,
  (state, mediationId) => mediationId,
  (recommendations, mediationId) => {
    recommendations = recommendations.map((r, index) =>
      Object.assign({}, r, { index })
    )
    // TODO: add headerColor
    if (mediationId)
      recommendations = recommendations.filter(
        r => r.mediationId === mediationId
      )
    return recommendations
  }
)((state, offererId, mediationId) => `${offererId || ''}/${mediationId || ''}`)
