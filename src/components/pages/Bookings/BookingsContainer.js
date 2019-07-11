import { connect } from 'react-redux'
import { compose } from 'redux'

import Bookings from './Bookings'
import {
  withFrenchQueryRouter,
  withRedirectToSigninWhenNotAuthenticated,
} from '../../hocs'
import { API_URL } from '../../../utils/config'

const buildPathToReservationFile = (isFilterByDigitalVenues, selectedVenue) => {
  let pathToFile = `${API_URL}/bookings/csv`
  let filtersToApply = []

  if (isFilterByDigitalVenues) {
    filtersToApply.push('onlyDigitalVenues=true')
  }

  if (selectedVenue && selectedVenue !== 'all') {
    filtersToApply.push(`venueId=${selectedVenue}`)
  }

  if (filtersToApply.length > 0) {
    pathToFile += `?${filtersToApply.join('&')}`
  }

  return pathToFile
}

export const mapStateToProps = state => {
  const { bookingSummary = {} } = state
  const { selectedVenue, isFilterByDigitalVenues } = bookingSummary

  const pathToCsvFile = buildPathToReservationFile(
    isFilterByDigitalVenues,
    selectedVenue,
  )

  const showDownloadButton = !!(isFilterByDigitalVenues || selectedVenue)

  return {
    pathToCsvFile,
    showDownloadButton,
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(mapStateToProps)
)(Bookings)
