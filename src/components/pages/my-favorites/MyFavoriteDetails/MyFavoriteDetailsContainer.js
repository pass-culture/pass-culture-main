import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import selectFavoriteById from '../../../../selectors/selectFavoriteById'
import { favoriteNormalizer } from '../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { favoriteId } = params
  const needsToRequestGetData = typeof favoriteId !== 'undefined'
  const favorite = selectFavoriteById(state, favoriteId)
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
