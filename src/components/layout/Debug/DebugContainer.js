import { connect } from 'react-redux'
import { showModal } from 'redux-react-modals'

import Debug from './Debug'

export default connect(
  null,
  { dispatchShowModal: showModal }
)(Debug)
