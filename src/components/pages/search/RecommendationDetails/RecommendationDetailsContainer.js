import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import selectRecommendationByOfferIdAndMediationId from '../../../../selectors/selectRecommendationByOfferIdAndMediationId'
import { recommendationNormalizer } from '../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = selectRecommendationByOfferIdAndMediationId(state, offerId, mediationId)
  const needsToRequestGetData = typeof offerId !== 'undefined'
  const hasReceivedData = typeof recommendation !== 'undefined'
  return {
    hasReceivedData,
    needsToRequestGetData,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params
  return {
    requestGetData: handleForceDetailsVisible => {
      let apiPath = `/recommendations/offers/${offerId}`
      if (mediationId) {
        apiPath = `${apiPath}?mediationId=${mediationId}`
      }

      dispatch(
        requestData({
          apiPath,
          handleSuccess: handleForceDetailsVisible,
          normalizer: recommendationNormalizer,
        })
      )
    },
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(DetailsContainer)
