import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Home from './Home'
import { selectCurrentUser } from '../../../redux/selectors/data/usersSelectors'
import { connect } from 'react-redux'
import { compose } from 'redux'

const mapStateToProps = state => ({
  user: selectCurrentUser(state)
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Home)
