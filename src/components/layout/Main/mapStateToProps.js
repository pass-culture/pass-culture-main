import { selectCurrentUser } from '../../../selectors/data/usersSelectors'

function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default mapStateToProps
