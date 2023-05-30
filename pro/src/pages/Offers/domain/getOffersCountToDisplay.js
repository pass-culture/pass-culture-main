export const getOffersCountToDisplay = offersCount =>
  offersCount <= 2 ? offersCount.toString() : '500+'
