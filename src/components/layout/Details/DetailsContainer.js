import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Details from './Details'
import areDetailsVisible from '../../../helpers/areDetailsVisible'

export const mapStateToProps = (state, { match }) => ({
  areDetails: areDetailsVisible(match),
})

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Details)
