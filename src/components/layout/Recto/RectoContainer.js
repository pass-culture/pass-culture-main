import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Recto from './Recto'
import selectMediationById from '../../../selectors/selectMediationById'
import selectMediationByMatch from '../../../selectors/selectMediationByMatch'
import selectThumbUrlByMatch from '../../../selectors/selectThumbUrlByMatch'

const mapStateToProps = (state, ownProps) => {
  const { match, recommendation } = ownProps

  let mediation = recommendation
    ? selectMediationById(state, recommendation.mediationId)
    : selectMediationByMatch(state, match) || {}

  const { frontText } = mediation || {}
  const withMediation = typeof mediation !== "undefined"

  const thumbUrl = recommendation
    ? recommendation.thumbUrl
    : selectThumbUrlByMatch(state, match)

  return {
    frontText,
    thumbUrl,
    withMediation
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Recto)
