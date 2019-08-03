import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoContentTuto from './VersoContentTuto'
import selectThumbUrlByMatch from '../../../../../selectors/selectThumbUrlByMatch'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const thumbUrl = selectThumbUrlByMatch(state, match)
  return {
    imageURL: thumbUrl
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoContentTuto)
