import { connect } from 'react-redux'
import { compose } from 'redux'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Tutorials from './Tutorials'
import { updateCurrentUser } from '../../../redux/actions/currentUser'

export const mergeProps = (stateProps, { updateCurrentUser, ...dispatchProps }, { history }) => {
  return {
    ...stateProps,
    ...dispatchProps,
    saveUserHasSeenTutorials: async () => {
      await updateCurrentUser({
        hasSeenTutorials: true,
      })
      history.push('/decouverte')
    },
  }
}

export default compose(
  withRequiredLogin,
  connect(
    null,
    { updateCurrentUser },
    mergeProps
  )
)(Tutorials)
