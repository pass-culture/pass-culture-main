import {compose} from 'redux'
import {connect} from 'react-redux'
import {withFrenchQueryRouter} from 'components/hocs'

import {FilterByDate} from './FilterByDate'

export const mapDispatchToProps = (dispatch) => ({
  selectBookingsForDate: (date) => {
    dispatch(
      {
        payload: date,
        type: 'BOOKING_SUMMARY_SELECT_DATE',
      }
    )
  }
})

export const mapStateToProps = (state) => {
  return {
    date: state.bookingSummary.selectOffersSince,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(FilterByDate)
