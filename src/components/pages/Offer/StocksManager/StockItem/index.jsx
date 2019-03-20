import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import mapStateToProps from './mapStateToProps'

import RawStockItem from './RawStockItem'

export default compose(
  withQueryRouter,
  connect(mapStateToProps)
)(RawStockItem)
