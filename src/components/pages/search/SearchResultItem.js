import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import RawSearchResultItem from './RawSearchResultItem'

export default compose(
  withRouter,
  connect()
)(RawSearchResultItem)
