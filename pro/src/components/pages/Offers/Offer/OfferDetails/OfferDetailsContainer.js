import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import {
  selectCurrentUser,
  selectIsUserAdmin,
} from 'store/selectors/data/usersSelectors'

import OfferDetails from './OfferDetails'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
  userEmail: selectCurrentUser(state).email,
})

export default compose(withRouter, connect(mapStateToProps))(OfferDetails)
