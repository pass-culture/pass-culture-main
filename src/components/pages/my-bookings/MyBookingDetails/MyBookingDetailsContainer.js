import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import DetailsContainer from '../../../layout/Details/DetailsContainer'
import selectBookingById from '../../../../selectors/selectBookingById'
import { bookingNormalizer } from '../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { bookingId } = params
  const needsToRequestGetData = typeof bookingId !== 'undefined'
  const booking = selectBookingById(state, bookingId)
  const hasReceivedData = typeof booking !== 'undefined'
  return {
    hasReceivedData,
    needsToRequestGetData,
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestGetData: handleSuccess => {
      const { match } = ownProps
      const { params } = match
      const { bookingId } = params
      let apiPath = `/bookings/${bookingId}`
      dispatch(
        requestData({
          apiPath,
          handleSuccess,
          normalizer: bookingNormalizer,
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
