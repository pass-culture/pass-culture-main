import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default mapStateToProps
