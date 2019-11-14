import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import isCancelView from '../../../helpers/isCancelView'
import Details from './Details'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const cancelView = isCancelView(match)

  return {
    cancelView,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Details)
