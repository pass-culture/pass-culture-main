import { selectCurrentUser } from 'with-login'

function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default mapStateToProps
