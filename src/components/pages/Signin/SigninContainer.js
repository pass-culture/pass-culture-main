import { connect } from 'react-redux'
import { withNotRequiredLogin } from '../../hocs'
import Signin from './Signin'
import selectIsFeatureActive from '../../router/selectors/selectIsFeatureActive'

export const mapStateToProps = state => {
  return {
    isAccountCreationAvailable: selectIsFeatureActive(state, 'API_SIRENE_AVAILABLE'),
  }
}

export default withNotRequiredLogin(connect(mapStateToProps)(Signin))
