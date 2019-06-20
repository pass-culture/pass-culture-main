import { connect } from 'react-redux'
import { compose } from 'redux'

import Bookings from './Bookings'
import { withFrenchQueryRouter, withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'

export const mapStateToProps = state => {
  return {
    isFilterByDigitalVenues: state.bookingSummary.isFilterByDigitalVenues,
    selectedVenue: state.bookingSummary.selectedVenue,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Bookings)
