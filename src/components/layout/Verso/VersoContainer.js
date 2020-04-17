import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectOfferByRouterMatch } from '../../../redux/selectors/data/offersSelectors'
import Verso from './Verso'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const { name: offerName, type: offerType, venue } = offer
  const { name: venueName, publicName: venuePublicName } = venue || {}
  const offerVenueNameOrPublicName = venuePublicName || venueName

  return {
    offerName,
    offerType,
    offerVenueNameOrPublicName,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Verso)
