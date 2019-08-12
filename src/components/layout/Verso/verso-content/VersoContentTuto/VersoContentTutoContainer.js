import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoContentTuto from './VersoContentTuto'
import selectThumbUrlByRouterMatch from '../../../../../selectors/selectThumbUrlByRouterMatch'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const thumbUrl = selectThumbUrlByRouterMatch(state, match)
  return {
    imageURL: thumbUrl,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoContentTuto)
