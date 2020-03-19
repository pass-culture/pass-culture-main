import _withLogin, {
  getCurrentUserUUID,
  resolveCurrentUser,
  selectCurrentUser,
} from 'with-react-login'
import { connect } from 'react-redux'

const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

const withLogin = config =>
  _withLogin({ ...config, ...{ withDispatcher: connect(mapStateToProps) } })

export { getCurrentUserUUID, mapStateToProps, resolveCurrentUser, selectCurrentUser }

export default withLogin
