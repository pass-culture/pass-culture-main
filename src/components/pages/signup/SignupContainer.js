import { compose } from 'redux'

import { withNotRequiredLogin, withFeatures } from '../../hocs'

import Signup from './Signup'

export default compose(
  withFeatures({ requiredFeatureNames: ['WEBAPP_SIGNUP'] }),
  withNotRequiredLogin
)(Signup)
