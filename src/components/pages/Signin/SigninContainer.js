import { connect } from 'react-redux'
import { withNotRequiredLogin } from '../../hocs'
import Signin from './Signin'
import { isAPISireneAvailable } from '../../../selectors/data/featuresSelectors'

export const mapStateToProps = state => {
  return {
    isAccountCreationAvailable: isAPISireneAvailable(state),
  }
}

export default withNotRequiredLogin(connect(mapStateToProps)(Signin))
