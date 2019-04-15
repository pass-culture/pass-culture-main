import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import VenueProvidersManager from './VenueProvidersManager'
import mapStateToProps from './mapStateToProps'

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VenueProvidersManager)
