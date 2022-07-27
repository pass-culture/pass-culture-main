import { connect } from 'react-redux'

import { selectCurrentUser, selectIsUserAdmin } from 'store/user/selectors'

import OfferDetails from './OfferDetails'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
  userEmail: selectCurrentUser(state).email,
})

export default connect(mapStateToProps)(OfferDetails)
