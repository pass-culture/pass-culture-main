import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoContentOffer from './VersoContentOffer'
import mapDispatchToProps from './mapDispatchToProps'
import mapStateToProps from './mapStateToProps'

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(VersoContentOffer)
