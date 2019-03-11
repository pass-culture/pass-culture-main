import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import mapStateToProps from './mapStateToProps'

import RawEventOccurrenceAndStockItem from './RawIndex'

export default compose(
  withRouter,
  connect(mapStateToProps)
)(RawEventOccurrenceAndStockItem)
