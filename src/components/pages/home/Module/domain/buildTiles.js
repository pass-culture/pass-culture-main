export const buildArrayOf = ({ cover, hits }) => {
  let arrayOfPairedOffers = []
  if (cover) {
    arrayOfPairedOffers.push([cover])
  }

  let pairedOffers = []
  for (let i = 0; i < hits.length; i++) {
    if (pairedOffers.length === 1) {
      pairedOffers.push(hits[i])
      arrayOfPairedOffers.push(pairedOffers)
      pairedOffers = []
    } else {
      const hasReachedLastItem = i === hits.length - 1
      if (hasReachedLastItem) {
        arrayOfPairedOffers.push([hits[i]])
      } else {
        pairedOffers.push(hits[i])
      }
    }
  }
  return arrayOfPairedOffers
}
