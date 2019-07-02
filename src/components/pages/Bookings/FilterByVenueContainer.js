import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import { connect } from 'react-redux'
import { withFrenchQueryRouter } from 'components/hocs'

import { FilterByVenue } from './FilterByVenue'
import selectNonVirtualVenues from './selectNonVirtualVenues'

export const mapDispatchToProps = dispatch => ({
  loadVenues: () => {
    dispatch(
      requestData({
        apiPath: `/venues`,
        stateKey: 'venues',
        method: 'GET',
      })
    )
  },
  selectOnlyDigitalVenues: payload => {
    dispatch({
      payload,
      type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
    })
  },
  selectBookingsForVenues: venueId => {
    dispatch({
      payload: venueId,
      type: 'BOOKING_SUMMARY_SELECT_VENUE',
    })
  },
})

export const mapStateToProps = state => {

  const { data = {} } = state;
  const { venues } = data
  const { bookingSummary = {} } = state;

  const allVenuesOption = {
    name: 'Tous les lieux',
    id: 'all',
  }

  const nonVirtualVenues = selectNonVirtualVenues(state, venues)
  const venuesOptions = [allVenuesOption, ...nonVirtualVenues]

  return {
    isDigital: state.bookingSummary.isFilterByDigitalVenues,
    venueId: bookingSummary.selectedVenue,
    venuesOptions,
  }
}

export default compose(
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(FilterByVenue)
