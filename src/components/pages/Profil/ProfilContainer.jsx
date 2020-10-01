import { compose } from 'redux'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { withRequiredLogin } from '../../hocs'
import Profil from './Profil'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(withRequiredLogin, connect(mapStateToProps))(Profil)
