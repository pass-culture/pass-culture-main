import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Tutorials from './Tutorials'

export const mapDispatchToProps = dispatch => ({
  saveUserHasSeenTutorials: handleSuccess => {
    dispatch(
      requestData({
        apiPath: '/users/current',
        body: {
          hasSeenTutorials: true,
        },
        handleSuccess,
        method: 'PATCH',
      })
    )
  },
})

export const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const { history } = ownProps
  return {
    ...stateProps,
    ...dispatchProps,
    redirectToDiscovery: () => {
      history.push('/decouverte')
    },
  }
}

export default compose(
  withRequiredLogin,
  connect(
    null,
    mapDispatchToProps,
    mergeProps
  )
)(Tutorials)
