import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import { favoriteNormalizer } from '../../../../utils/normalizers'

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
    null,
    mapDispatchToProps
  )
)(DetailsContainer)
