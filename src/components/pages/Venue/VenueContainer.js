import { connect } from 'react-redux'
import { compose } from 'redux'

import Venue from './Venue'
import mapDispatchToProps from './mapDispatchToProps'
import mapStateToProps from './mapStateToProps'
import {
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
} from 'components/hocs'

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Venue)
