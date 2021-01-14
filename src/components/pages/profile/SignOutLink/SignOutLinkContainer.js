import { connect } from 'react-redux'

import { resetCurrentUser } from '../../../../redux/actions/currentUser'
import { updateSeedLastRequestTimestamp } from '../../../../redux/actions/pagination'
import { reinitializeData } from '../../../../utils/fetch-normalize-data/reducers/data/actionCreators'
import SignOutLink from './SignOutLink'

const resetSeedLastRequestTimestamp = date => updateSeedLastRequestTimestamp(date)

const reinitializeDataExceptFeatures = () => reinitializeData({ excludes: ['features'] })

export const mapDispatchToProps = dispatch => ({
  resetSeedLastRequestTimestamp: date => {
    dispatch(resetSeedLastRequestTimestamp(date))
  },
  reinitializeDataExceptFeatures: () => {
    dispatch(reinitializeDataExceptFeatures())
    dispatch(resetCurrentUser())
  },
})

export default connect(null, mapDispatchToProps)(SignOutLink)
