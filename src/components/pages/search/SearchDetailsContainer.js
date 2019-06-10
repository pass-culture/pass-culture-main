import { connect } from 'react-redux'

import { selectCurrentSearchRecommendation } from '../../../selectors'
import { SearchDetails } from './SearchDetails'

function mapStateToProps(state, ownProps) {
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = selectCurrentSearchRecommendation(
    state,
    offerId,
    mediationId
  )

  return { recommendation }
}

export const SearchDetailsContainer = connect(mapStateToProps)(SearchDetails)
