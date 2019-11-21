import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectMediationByRouterMatch } from '../../../selectors/data/mediationsSelectors'
import { selectOfferByRouterMatch } from '../../../selectors/data/offersSelectors'
import { ROOT_PATH } from '../../../utils/config'
import Verso from './Verso'

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`
const backgroundColor = 'black'

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
