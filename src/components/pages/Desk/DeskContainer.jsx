import Desk from './Desk'
import { compose } from 'redux'
import { connect } from 'react-redux'

import { withRequiredLogin } from 'components/hocs'

export default compose(
  withRequiredLogin,
  connect()
)(Desk)
