import { selectCurrentUser } from 'with-react-redux-login'

function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

export default mapStateToProps
