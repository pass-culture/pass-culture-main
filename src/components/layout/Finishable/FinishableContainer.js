import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Finishable from './Finishable'
import selectIsFinishedByMatch from '../../../selectors/selectIsFinishedByMatch'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const isFinished = selectIsFinishedByMatch(state, match)
  return {
    isFinished
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Finishable)
