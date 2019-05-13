import { connect } from 'react-redux'
import { compose } from 'redux'

import StockItem from './StockItem'
import mapStateToProps from './mapStateToProps'
import { withFrenchQueryRouter } from 'components/hocs'

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StockItem)
