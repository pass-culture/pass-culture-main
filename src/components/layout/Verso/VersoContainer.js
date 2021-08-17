import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { selectOfferByRouterMatch } from '../../../redux/selectors/data/offersSelectors'
import { selectSubcategory } from '../../../redux/selectors/data/categoriesSelectors'

import Verso from './Verso'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const offer = selectOfferByRouterMatch(state, match) || {}
  const { name: offerName, venue } = offer
  const { name: venueName, publicName: venuePublicName } = venue || {}
  const offerVenueNameOrPublicName = venuePublicName || venueName
  const subcategory = selectSubcategory(state, offer)

  return {
    offerName,
    subcategory,
    offerVenueNameOrPublicName,
  }
}

export default compose(withRouter, connect(mapStateToProps))(Verso)
