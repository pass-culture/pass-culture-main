import { selectCurrentUser } from 'with-login'
import { connect } from 'react-redux'
import ProfileForm from './ProfileForm'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default connect(mapStateToProps)(ProfileForm)
