import { connect } from 'react-redux'
import { compose } from 'redux'

import mapStateToProps from './mapStateToProps'
import RawStockItem from './RawStockItem'
import { withFrenchQueryRouter } from 'components/hocs'

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(RawStockItem)
