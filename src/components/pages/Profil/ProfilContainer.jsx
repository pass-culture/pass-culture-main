import { connect } from 'react-redux'
import { compose } from 'redux'

import { withRequiredLogin } from 'components/hocs'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Profil from './Profil'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export default compose(withRequiredLogin, connect(mapStateToProps))(Profil)
