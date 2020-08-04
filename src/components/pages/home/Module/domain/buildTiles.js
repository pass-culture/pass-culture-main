import { CONTENTFUL_PARAMETERS } from '../../domain/parseAlgoliaParameters'

export const buildArrayOf = ({ algolia = {}, cover, hits, nbHits }) => {
  let arrayOfPairedOffers = []
  if (cover) {
    arrayOfPairedOffers.push([cover])
  }

  const seeMoreOffers = hits.length < nbHits
  const seeMoreTileCanBeDisplayed = !(
    algolia[CONTENTFUL_PARAMETERS.TAGS] ||
    algolia[CONTENTFUL_PARAMETERS.BEGINNING_DATETIME] ||
    algolia[CONTENTFUL_PARAMETERS.ENDING_DATETIME]
  )

  let pairedOffers = []
  for (let i = 0; i < hits.length; i++) {
    const hasReachedLastItem = i === hits.length - 1

    if (pairedOffers.length === 1) {
      pairedOffers.push(hits[i])
      arrayOfPairedOffers.push(pairedOffers)
      pairedOffers = []

      if (hasReachedLastItem && seeMoreOffers && seeMoreTileCanBeDisplayed) {
        arrayOfPairedOffers.push([true])
      }
    } else {
      if (hasReachedLastItem) {
        if (seeMoreOffers && seeMoreTileCanBeDisplayed) {
          arrayOfPairedOffers.push([hits[i], true])
        } else {
          arrayOfPairedOffers.push([hits[i]])
        }
      } else {
        pairedOffers.push(hits[i])
      }
    }
  }


  return arrayOfPairedOffers
}
