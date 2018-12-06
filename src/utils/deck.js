export const PREVIOUS_NEXT_LIMIT = 2
export default PREVIOUS_NEXT_LIMIT

export const isThereRecommendations = (
  recommendations,
  previousProps,
  currentRecommendation
) =>
  !recommendations ||
  !previousProps.recommendations ||
  recommendations === previousProps.recommendations ||
  !currentRecommendation ||
  !previousProps.currentRecommendation ||
  currentRecommendation.index === previousProps.currentRecommendation.index
