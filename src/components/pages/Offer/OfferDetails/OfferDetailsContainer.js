import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectIsUserAdmin } from 'store/selectors/data/usersSelectors'

import OfferDetails from './OfferDetails'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
})

export default compose(withRouter, connect(mapStateToProps))(OfferDetails)
