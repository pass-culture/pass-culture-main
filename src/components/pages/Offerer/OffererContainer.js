import { connect } from 'react-redux'
import { compose } from 'redux'

import Offerer from './Offerer'
import mapStateToProps from './mapStateToProps'
<<<<<<< HEAD
import withFrenchQueryRouter from '../../hocs/withFrenchQueryRouter'
import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'
=======
import {
  withFrenchQueryRouter,
  withRequiredLogin,
} from 'components/hocs'
>>>>>>> (pC-2025) renamed withLogin hocs

export default compose(
  withRequiredLogin,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Offerer)
