import { connect } from 'react-redux'
import { compose } from 'redux'

import BankFields from './BankFields'
import mapStateToProps from './mapStateToProps'
import { withFrenchQueryRouter } from 'components/hocs'

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(BankFields)
