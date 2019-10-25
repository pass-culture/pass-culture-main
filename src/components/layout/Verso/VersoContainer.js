import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Verso from './Verso'
import getHeaderColor from '../../../utils/colors'
import selectMediationByRouterMatch from '../../../selectors/selectMediationByRouterMatch'
import { selectOfferByRouterMatch } from '../../../selectors/data/offersSelector'
import { ROOT_PATH } from '../../../utils/config'

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`

export const checkIsTuto = mediation => {
  const { tutoIndex } = mediation || {}
  return Boolean(typeof tutoIndex === 'number')
}

export const getContentInlineStyle = (isTuto, backgroundColor) => {
  let result = { backgroundImage }
  if (isTuto && backgroundColor) result = { ...result, backgroundColor }
  return result
}

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const mediation = selectMediationByRouterMatch(state, match) || {}
  const firstThumbDominantColor = offer.firstThumbDominantColor || mediation.firstThumbDominantColor

  const backgroundColor = getHeaderColor(firstThumbDominantColor)
  const isTuto = checkIsTuto(mediation)
  const contentInlineStyle = getContentInlineStyle(isTuto, backgroundColor)
  const { name: offerName, type: offerType, venue } = offer
  const { name: venueName, publicName: venuePublicName } = venue || {}
  const offerVenueNameOrPublicName = venuePublicName || venueName

  return {
    backgroundColor,
    contentInlineStyle,
    isTuto,
    offerName,
    offerType,
    offerVenueNameOrPublicName,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Verso)
