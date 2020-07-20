import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Home from './Home'
import { selectCurrentUser } from '../../../redux/selectors/currentUserSelector'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectUserGeolocation } from '../../../redux/selectors/geolocationSelectors'

const mapStateToProps = state => ({
  geolocation: selectUserGeolocation(state),
  user: selectCurrentUser(state)
})

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Home)
