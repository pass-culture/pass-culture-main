import { connect } from 'react-redux'
import { compose } from 'redux'

import Offerer from './Offerer'
import mapStateToProps from './mapStateToProps'
import { withRequiredLogin } from '../../hocs'

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Offerer)
