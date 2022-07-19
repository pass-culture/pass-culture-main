import { selectCurrentUser, selectIsUserAdmin } from 'store/user/selectors'

import OfferDetails from './OfferDetails'
import { connect } from 'react-redux'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
  userEmail: selectCurrentUser(state).email,
})

export default connect(mapStateToProps)(OfferDetails)
