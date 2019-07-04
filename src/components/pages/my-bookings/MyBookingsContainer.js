import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import { withRequiredLogin } from '../../hocs'
import MyBookings from './MyBookings'
import { selectSoonBookings, selectMyBookings } from '../../../selectors'

export const mapStateToProps = state => {
  const myBookings = selectMyBookings(state)
  const soonBookings = selectSoonBookings(state)
  return { myBookings, soonBookings }
}

export const mapDispatchToProps = dispatch => ({
  getMyBookings: (handleFail, handleSuccess) => {
    dispatch(
      requestData({
        apiPath: '/bookings',
        handleFail,
        handleSuccess,
        stateKey: 'bookings',
      })
    )
  },
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(MyBookings)
