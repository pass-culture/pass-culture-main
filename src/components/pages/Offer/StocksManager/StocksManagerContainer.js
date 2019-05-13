import { connect } from 'react-redux'
import { compose } from 'redux'

import StocksManager from './StocksManager'
import mapStateToProps from './mapStateToProps'
import { withFrenchQueryRouter } from 'components/hocs'

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(StocksManager)
