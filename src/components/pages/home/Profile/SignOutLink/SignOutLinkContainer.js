import { connect } from 'react-redux'

import { updateSeedLastRequestTimestamp } from '../../../../../redux/actions/pagination'
import SignOutLink from './SignOutLink'
import { selectReadRecommendations } from '../../../../../redux/selectors/data/readRecommendationsSelectors'
import { resetCurrentUser } from '../../../../../redux/actions/currentUser'
import { reinitializeData } from '../../../../../utils/fetch-normalize-data/reducers/data/actionCreators'

const resetSeedLastRequestTimestamp = date => updateSeedLastRequestTimestamp(date)

const reinitializeDataExceptFeatures = () => reinitializeData({ excludes: ['features'] })

const mapStateToProps = state => ({
  readRecommendations: selectReadRecommendations(state),
})

export const mapDispatchToProps = dispatch => ({
  resetSeedLastRequestTimestamp: date => {
    dispatch(resetSeedLastRequestTimestamp(date))
  },
  reinitializeDataExceptFeatures: () => {
    dispatch(reinitializeDataExceptFeatures())
    dispatch(resetCurrentUser())
  },
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SignOutLink)
