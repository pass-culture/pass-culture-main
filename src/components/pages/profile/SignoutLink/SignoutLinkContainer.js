import { connect } from 'react-redux'
import { reinitializeData, requestData } from 'redux-thunk-data'

import SignoutLink from './SignoutLink'
import { updateSeedLastRequestTimestamp } from '../../../../redux/actions/pagination'

export const mapDispatchToProps = dispatch => ({
  onSignOutClick: (historyPush, readRecommendations) => () => {
    const handleRequestSignout = () => {
      const handleSuccessAfterSignOut = () => {
        historyPush('/connexion')
        dispatch(reinitializeData({ excludes: ['features'] }))
      }
      dispatch(
        requestData({
          apiPath: '/users/signout',
          handleSuccess: handleSuccessAfterSignOut,
        })
      )
      dispatch(updateSeedLastRequestTimestamp(Date.now()))
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
)(SignoutLink)
