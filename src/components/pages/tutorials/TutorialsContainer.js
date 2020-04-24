import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Tutorials from './Tutorials'

export const mapDispatchToProps = dispatch => ({
  saveUserHasSeenTutorials: () => {
    dispatch(
      requestData({
        apiPath: '/users/current',
        body: {
          hasSeenTutorials: true,
        },
        method: 'PATCH',
      })
    )
  },
})

export default compose(
  withRequiredLogin,
  connect(
    null,
    mapDispatchToProps
  )
)(Tutorials)
