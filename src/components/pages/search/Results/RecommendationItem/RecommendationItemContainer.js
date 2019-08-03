import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import RecommendationItem from './RecommendationItem'
import { getOfferIdAndMediationIdUrlElement } from '../../../../../helpers'
import selectOfferById from '../../../../../selectors/selectOfferById'
import { recommendationNormalizer } from '../../../../../utils/normalizers'

export const onSuccessLoadRecommendationDetails = ownProps => () => {
  const { history, location, recommendation } = ownProps
  const { pathname, search } = location
  const urlElement = getOfferIdAndMediationIdUrlElement(recommendation)
  const linkURL = `${pathname}/details/${urlElement}${search}`
  history.push(linkURL)
}

export const mapStateToProps = (state, ownProps) => {
  const { recommendation } = ownProps
  const { offerId } = recommendation
  const offer = selectOfferById(state, offerId)
  return {
    offer,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { recommendation } = ownProps
  return {
    handleMarkSearchRecommendationsAsClicked: () => {
      const config = {
        apiPath: `/recommendations/${recommendation.id}`,
        body: { isClicked: true },
        handleSuccess: onSuccessLoadRecommendationDetails(ownProps),
        method: 'PATCH',
        normalizer: recommendationNormalizer,
      }
      dispatch(requestData(config))
    },
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(RecommendationItem)
