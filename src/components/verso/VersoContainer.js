import get from 'lodash.get'
import { connect } from 'react-redux'

import { ROOT_PATH } from '../../utils/config'
import Verso from './Verso'
import { getHeaderColor } from '../../utils/colors'

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`

export const getContentInlineStyle = (isTuto, backgroundColor) => {
  let result = { backgroundImage }
  if (isTuto && backgroundColor) result = { ...result, backgroundColor }
  return result
}

export const checkIsTuto = recommendation => {
  const tutoIndex = get(recommendation, 'mediation.tutoIndex')
  const result = Boolean(typeof tutoIndex === 'number')
  return result
}

export const getOfferVenueNameOrPublicName = recommendation => {
  const venueName = get(recommendation, 'offer.venue.name', null)
  const venuePublicName = get(recommendation, 'offer.venue.publicName', null)

  return venuePublicName || venueName
}

export const getOfferName = recommendation =>
  get(recommendation, 'offer.name', null)

export const getBackgroundColor = recommendation => {
  const firstThumbDominantColor = get(recommendation, 'firstThumbDominantColor')
  return getHeaderColor(firstThumbDominantColor)
}

export const mapStateToProps = (state, { recommendation }) => {
  if (!recommendation) {
    const msg = 'Props recommandation is missing in VersoContainer component'
    throw new Error(msg)
  }
  const backgroundColor = getBackgroundColor(recommendation)
  const isTuto = checkIsTuto(recommendation)
  const offerVenueNameOrPublicName = getOfferVenueNameOrPublicName(
    recommendation
  )
  const offerName = getOfferName(recommendation)

  const contentInlineStyle = getContentInlineStyle(isTuto, backgroundColor)

  const draggable = get(state, 'card.draggable')
  const areDetailsVisible = get(state, 'card.areDetailsVisible')
  const imageURL = get(recommendation, 'thumbUrl')

  return {
    areDetailsVisible,
    backgroundColor,
    contentInlineStyle,
    draggable,
    imageURL,
    isTuto,
    offerName,
    offerVenueNameOrPublicName,
  }
}

export default connect(mapStateToProps)(Verso)
