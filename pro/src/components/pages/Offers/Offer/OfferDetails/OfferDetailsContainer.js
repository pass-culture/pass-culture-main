import {
  selectCurrentUser,
  selectIsUserAdmin,
} from 'store/selectors/data/usersSelectors'

import OfferDetails from './OfferDetails'
import { connect } from 'react-redux'

const mapStateToProps = state => ({
  isUserAdmin: selectIsUserAdmin(state),
  userEmail: selectCurrentUser(state).email,
})

export default connect(mapStateToProps)(OfferDetails)
