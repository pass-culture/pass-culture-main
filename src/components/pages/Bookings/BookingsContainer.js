import { connect } from 'react-redux'
import { compose } from 'redux'

import Bookings from './Bookings'
import { withRequiredLogin } from '../../hocs'
import { API_URL } from '../../../utils/config'

const buildPathToBookingFile = (
  bookingsFrom,
  bookingsTo,
  isFilteredByDigitalVenues,
  offerId,
  venueId
) => {
  let pathToFile = `${API_URL}/bookings/csv`
  let filtersToApply = []

  if (isFilteredByDigitalVenues) {
    filtersToApply.push('onlyDigitalVenues=true')
  }

  if (venueId && venueId !== 'all') {
    filtersToApply.push(`venueId=${venueId}`)
  }

  if (offerId && offerId !== 'all') {
    filtersToApply.push(`offerId=${offerId}`)
  }

  if (bookingsFrom) {
    filtersToApply.push(`dateFrom=${bookingsFrom}`)
  }

  if (bookingsTo) {
    filtersToApply.push(`dateTo=${bookingsTo}`)
  }

  if (filtersToApply.length > 0) {
    pathToFile += `?${filtersToApply.join('&')}`
  }

  return pathToFile
}

export const mapStateToProps = state => {
  const { bookingSummary = {} } = state
  const { bookingsFrom, bookingsTo, isFilteredByDigitalVenues, offerId, venueId } = bookingSummary

  const pathToCsvFile = buildPathToBookingFile(
    bookingsFrom,
    bookingsTo,
    isFilteredByDigitalVenues,
    offerId,
    venueId
  )

  const showButtons =
    !!(isFilteredByDigitalVenues && offerId && bookingsFrom && bookingsTo) ||
    !!(venueId && offerId && bookingsFrom && bookingsTo) ||
    venueId === 'all' ||
    offerId === 'all'

  const showOfferSection = venueId !== 'all' && (!!venueId || !!isFilteredByDigitalVenues)

  return {
    pathToCsvFile,
    showButtons,
    showOfferSection,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Bookings)
