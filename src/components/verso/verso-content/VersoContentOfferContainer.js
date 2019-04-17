/* eslint
  react/jsx-one-expression-per-line: 0 */
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoContentOffer from './VersoContentOffer'
import mapStateToProps from './mapStateToProps'

const VersoContentOfferContainer = compose(
  withRouter,
  connect(mapStateToProps)
)(VersoContentOffer)

export default VersoContentOfferContainer
