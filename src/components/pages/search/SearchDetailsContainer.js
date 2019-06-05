import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import get from 'lodash.get'

import { selectCurrentSearchRecommendation } from '../../../selectors'
import { SearchDetails } from './SearchDetails'

function mapStateToProps(state, ownProps) {
  const { match } = ownProps
  const offerId = get(match, 'params.offerId')
  const mediationId = get(match, 'params.mediationId')
  const recommendation = selectCurrentSearchRecommendation(
    state,
    offerId,
    mediationId
  )

  return { recommendation }
}

export const SearchDetailsContainer = compose(
  withRouter,
  connect(mapStateToProps)
)(SearchDetails)
