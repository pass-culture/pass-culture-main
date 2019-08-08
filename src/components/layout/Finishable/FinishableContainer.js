import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Finishable from './Finishable'
import selectIsFinishedByRouterMatch from '../../../selectors/selectIsFinishedByRouterMatch'

const mapStateToProps = (state, { match }) => ({
  isFinished: selectIsFinishedByRouterMatch(state, match),
})

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
