import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import withTracking from '../../hocs/withTracking'
import Home from './Home'
import { selectCurrentUser } from '../../../redux/selectors/currentUserSelector'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectUserGeolocation } from '../../../redux/selectors/geolocationSelectors'
import { updateCurrentUser } from '../../../redux/actions/currentUser'

export const mapStateToProps = state => ({
  geolocation: selectUserGeolocation(state),
  user: selectCurrentUser(state),
})

export const mapDispatchToProps = () => ({ updateCurrentUser })

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackAllModulesSeen: numberOfModules => {
      ownProps.tracking.trackEvent({
        action: 'AllModulesSeen',
        name: `Number of modules: ${numberOfModules}`,
      })
    },
  }
}

export default compose(
  withRequiredLogin,
  withTracking('Home'),
  connect(
    mapStateToProps,
    mapDispatchToProps,
    mergeProps
  )
)(Home)
