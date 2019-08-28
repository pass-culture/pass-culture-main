import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import { bookingNormalizer } from '../../../../utils/normalizers'

export const mapDispatchToProps = (dispatch, ownProps) => ({
  requestGetData: handleSuccess => {
    const { match } = ownProps
    const { params } = match
    const { bookingId } = params

    dispatch(
      requestData({
        apiPath: `/bookings/${bookingId}`,
        handleSuccess,
        normalizer: bookingNormalizer,
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
