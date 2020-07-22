import { connect } from 'react-redux'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import { getOffer } from '../repository/getOffer'

export const mapDispatchToProps = dispatch => ({
  getOfferById: offerId => {
    dispatch(getOffer(offerId))
  },
})

export default connect(
  null,
  mapDispatchToProps
)(DetailsContainer)
