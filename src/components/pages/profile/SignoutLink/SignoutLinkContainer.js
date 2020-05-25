import { connect } from 'react-redux'
import { reinitializeData, requestData } from 'redux-thunk-data'

import { updateSeedLastRequestTimestamp } from '../../../../redux/actions/pagination'
import SignoutLink from './SignoutLink'

const fetchSignOut = handleSuccess => requestData({
  apiPath: '/users/signout',
  handleSuccess: handleSuccess,
})

const fetchUpdateReadRecommendations = (readRecommendations, handleSignOut) => requestData({
  apiPath: '/recommendations/read',
  body: readRecommendations,
  handleSuccess: handleSignOut,
  handleFail: handleSignOut,
  method: 'PUT',
})

const resetSeedLastRequestTimestamp = date => updateSeedLastRequestTimestamp(date)

const reinitializeDataExceptFeatures = () => reinitializeData({ excludes: ['features'] })

export const mapDispatchToProps = dispatch => ({
  signOut: handleSuccess => {
    dispatch(
      fetchSignOut(handleSuccess)
    )
  },
  resetSeedLastRequestTimestamp: date => {
    dispatch(resetSeedLastRequestTimestamp(date))
  },
  reinitializeDataExceptFeatures: () => {
    dispatch(reinitializeDataExceptFeatures())
  },
  updateReadRecommendations: (readRecommendations, handleSignOut) => {
    dispatch(
      fetchUpdateReadRecommendations(readRecommendations, handleSignOut)
    )
  }
})

export default connect(
  null,
  mapDispatchToProps
)(SignoutLink)
