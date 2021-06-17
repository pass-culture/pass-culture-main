export const getOffersCountToDisplay = offersCount =>
  offersCount <= 200 ? offersCount.toString() : '200+'
