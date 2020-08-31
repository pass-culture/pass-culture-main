import { connect } from 'react-redux'
import PersonalInformations from './PersonalInformations'
import { updateCurrentUser } from '../../../../../redux/actions/currentUser'

export default connect(
  null,
  { updateCurrentUser }
)(PersonalInformations)
