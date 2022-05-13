import OffererDetails from './OffererDetails'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const {
    params: { offererId },
  } = match
  const currentUser = selectCurrentUser(state)
  return {
    currentUser,
    offererId,
  }
}

export default connect(mapStateToProps)(OffererDetails)
