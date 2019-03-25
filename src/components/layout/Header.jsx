import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import RawHeader from './RawHeader'

const mapStateToProps = state => {
  const name = get(state, 'user.publicName')
  return {
    name,
    offerers: state.data.offerers,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawHeader)
