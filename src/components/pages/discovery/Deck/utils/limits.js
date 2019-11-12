export const NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD = 5

export const getNextLimit = (nbRecommendations) => {
  return nbRecommendations > 0 &&
    (NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD >= nbRecommendations - 1
      ? nbRecommendations - 1
      : nbRecommendations - 1 - NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD)
}
