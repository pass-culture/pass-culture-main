export const sortByOfferName = (firstRow, secondRow) => {
  const offerNameOne = firstRow.original.stock.offer_name
  const offerNameTwo = secondRow.original.stock.offer_name
  return offerNameOne.localeCompare(offerNameTwo)
}
