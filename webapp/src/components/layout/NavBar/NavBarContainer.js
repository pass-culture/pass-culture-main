import { connect } from 'react-redux'

import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import NavBar from './NavBar'

const mapStateToProps = state => ({
  isFeatureEnabled: featureName =>
    featureName ? !selectIsFeatureDisabled(state, featureName) : true,
})

export default connect(mapStateToProps)(NavBar)
