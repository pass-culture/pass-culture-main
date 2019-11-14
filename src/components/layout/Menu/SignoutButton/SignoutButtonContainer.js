import { connect } from 'react-redux'
import { requestData, reinitializeData } from 'redux-thunk-data'

import SignoutButton from './SignoutButton'
import { toggleMainMenu } from '../../../../reducers/menu'
import { updatePage, updateSeed } from '../../../../reducers/pagination'

export const mapDispatchToProps = dispatch => ({
  onSignOutClick: ({ history, readRecommendations }) => () => {
    const handleRequestSignout = () => {
      const handleSuccessAfterSignOut = () => {
        history.push('/connexion')
        dispatch(toggleMainMenu())
        dispatch(reinitializeData({ excludes: ['features'] }))
      }
      dispatch(
        requestData({
          apiPath: '/users/signout',
          handleSuccess: handleSuccessAfterSignOut,
        })
      )
      dispatch(
        updatePage(1)
      )
      dispatch(
        updateSeed(Math.random())
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
