import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import RawHeader from './RawHeader'
import offerersSelector from '../../selectors/offerers'

const mapStateToProps = state => {
  const name = get(state, 'user.publicName')
  const offerers = offerersSelector(state)
  return {
    name,
    offerers,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawHeader)
