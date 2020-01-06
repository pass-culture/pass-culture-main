import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { selectMediationByRouterMatch } from '../../../selectors/data/mediationsSelectors'
import { selectOfferByRouterMatch } from '../../../selectors/data/offersSelectors'
import Verso from './Verso'

export const checkIsTuto = mediation => {
  const { tutoIndex } = mediation || {}
  return Boolean(typeof tutoIndex === 'number')
}

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const mediation = selectMediationByRouterMatch(state, match) || {}

  const isTuto = checkIsTuto(mediation)
  const extraClassNameVersoContent = isTuto ? 'pc-theme-black' : 'verso-content'
  const { name: offerName, type: offerType, venue } = offer
  const { name: venueName, publicName: venuePublicName } = venue || {}
  const offerVenueNameOrPublicName = venuePublicName || venueName

  return {
    extraClassNameVersoContent,
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
