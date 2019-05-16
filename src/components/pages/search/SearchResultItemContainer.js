import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import SearchResultItem from './SearchResultItem'

export default compose(
  withRouter,
  connect()
)(SearchResultItem)
