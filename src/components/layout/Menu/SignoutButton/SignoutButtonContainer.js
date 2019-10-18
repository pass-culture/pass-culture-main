import { connect } from 'react-redux'
import { requestData, reinitializeData } from 'redux-thunk-data'

import SignoutButton from './SignoutButton'
import { toggleMainMenu } from '../../../../reducers/menu'

export const mapDispatchToProps = dispatch => ({
  onSignoutClick: ({ history, readRecommendations }) => () => {
    const handleRequestSignout = () => {
      const handleSuccessAfterSignout = () => {
        history.push('/connexion')
        dispatch(toggleMainMenu())
        dispatch(reinitializeData({ excludes: ['features'] }))
      }
      dispatch(
        requestData({
          apiPath: '/users/signout',
          handleSuccess: handleSuccessAfterSignout,
        })
      )
    }

    if (!readRecommendations || readRecommendations.length === 0) {
      handleRequestSignout()
    } else {
      dispatch(
        requestData({
          apiPath: '/recommendations/read',
          body: readRecommendations,
          handleFail: handleRequestSignout,
          handleSuccess: handleRequestSignout,
          method: 'PUT',
        })
      )
    }
  },
})

export default connect(
  null,
  mapDispatchToProps
)(SignoutButton)
