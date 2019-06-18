import { connect } from 'react-redux'
import { compose } from 'redux'

<<<<<<< HEAD
import withFrenchQueryRouter from '../../hocs/withFrenchQueryRouter'
import withRedirectToSigninWhenNotAuthenticated from '../../hocs/with-login/withRedirectToSigninWhenNotAuthenticated'
=======
import {
  withFrenchQueryRouter,
  withRequiredLogin,
} from 'components/hocs'
>>>>>>> (pC-2025) renamed withLogin hocs
import Offerers from './Offerers'

export const mapStateToProps = state => {
  return {
    pendingOfferers: state.data.pendingOfferers,
    offerers: state.data.offerers,
  }
}

export default compose(
  withRequiredLogin,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Offerers)
