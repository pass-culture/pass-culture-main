import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import { recommendationNormalizer } from '../../../../utils/normalizers'

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
    null,
    mapDispatchToProps
  )
)(DetailsContainer)
