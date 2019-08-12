import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Verso from './Verso'
import getHeaderColor from '../../../utils/colors'
import selectMediationByRouterMatch from '../../../selectors/selectMediationByRouterMatch'
import selectOfferByRouterMatch from '../../../selectors/selectOfferByRouterMatch'
import { ROOT_PATH } from '../../../utils/config'

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`

export const checkIsTuto = mediation => {
  const { tutoIndex } = mediation || {}
  const result = Boolean(typeof tutoIndex === 'number')
  return result
}

export const getContentInlineStyle = (isTuto, backgroundColor) => {
  let result = { backgroundImage }
  if (isTuto && backgroundColor) result = { ...result, backgroundColor }
  return result
}

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const mediation = selectMediationByRouterMatch(state, match) || {}
  const firstThumbDominantColor = offer.firstThumbDominantColor || mediation.firstThumbDominantColor
  const backgroundColor = getHeaderColor(firstThumbDominantColor)
  const isTuto = checkIsTuto(mediation)
  const contentInlineStyle = getContentInlineStyle(isTuto, backgroundColor)

  const { name: offerName, venue } = offer
  const { name: venueName, publicName: venuePublicName } = venue || {}
  const offerVenueNameOrPublicName = venuePublicName || venueName

  return {
    backgroundColor,
    contentInlineStyle,
    isTuto,
    offerName,
    offerVenueNameOrPublicName,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Verso)
