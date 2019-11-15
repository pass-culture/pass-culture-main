import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoContentTuto from './VersoContentTuto'
import { selectThumbUrlByRouterMatch } from '../../../../../selectors/data/thumbUrlSelector'

const VERSO_OVH_THUMB_SUFFIX = '_1'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const thumbUrl = selectThumbUrlByRouterMatch(state, match)
  return {
    imageURL: `${thumbUrl}${VERSO_OVH_THUMB_SUFFIX}`,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(VersoContentTuto)
