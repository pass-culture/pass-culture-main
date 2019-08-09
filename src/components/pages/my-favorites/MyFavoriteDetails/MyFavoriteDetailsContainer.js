import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import selectFavoriteByOfferIdAndMediationId from '../../../../selectors/selectFavoriteByOfferIdAndMediationId'
import { favoriteNormalizer } from '../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { offerId, mediationId } = params
  const needsToRequestGetData = typeof favoriteId !== 'undefined'
  const favorite = selectFavoriteByOfferIdAndMediationId(state, offerId, mediationId)
  const hasReceivedData = typeof favorite !== 'undefined'

  return {
    hasReceivedData,
    needsToRequestGetData,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => ({
  requestGetData: handleSuccess => {
    const { match } = ownProps
    const { params } = match
    const { favoriteId } = params

    dispatch(
      requestData({
        apiPath: `/favorites/${favoriteId}`,
        handleSuccess,
        normalizer: favoriteNormalizer,
      })
    )
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(DetailsContainer)
