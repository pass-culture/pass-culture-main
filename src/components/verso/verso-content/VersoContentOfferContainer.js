/* eslint
  react/jsx-one-expression-per-line: 0 */
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import VersoContentOffer from './VersoContentOffer'
import { isRecommendationFinished } from '../../../helpers'
import { selectBookables } from '../../../selectors/selectBookables'
import currentRecommendationSelector from '../../../selectors/currentRecommendation'

const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { mediationId, offerId } = match.params
  // recuperation de la recommandation
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )

  const bookables = selectBookables(state, recommendation, match)
  const isFinished = isRecommendationFinished(recommendation, offerId)
  return {
    bookables,
    isFinished,
    recommendation,
  }
}

const VersoContentOfferContainer = compose(
  withRouter,
  connect(mapStateToProps)
)(VersoContentOffer)

export default VersoContentOfferContainer
