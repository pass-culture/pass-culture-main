import { connect } from 'react-redux'
import { compose } from 'redux'

import Bookings from './Bookings'
import { withRequiredLogin } from '../../hocs'
import { API_URL } from '../../../utils/config'

const buildPathToBookingFile = (
  isFilterByDigitalVenues,
  selectedOffer,
  selectOffersFrom,
  selectOffersTo,
  selectedVenue
) => {
  let pathToFile = `${API_URL}/bookings/csv`
  let filtersToApply = []

  if (isFilterByDigitalVenues) {
    filtersToApply.push('onlyDigitalVenues=true')
  }

  if (selectedVenue && selectedVenue !== 'all') {
    filtersToApply.push(`venueId=${selectedVenue}`)
  }

  if (selectedOffer && selectedOffer !== 'all') {
    filtersToApply.push(`offerId=${selectedOffer}`)
  }

  if (selectOffersFrom) {
    filtersToApply.push(`dateFrom=${selectOffersFrom}`)
  }

  if (selectOffersTo) {
    filtersToApply.push(`dateTo=${selectOffersTo}`)
  }

  if (filtersToApply.length > 0) {
    pathToFile += `?${filtersToApply.join('&')}`
  }

  return pathToFile
}

export const mapStateToProps = state => {
  const { bookingSummary = {} } = state
  const {
    isFilterByDigitalVenues,
    selectedOffer,
    selectOffersFrom,
    selectOffersTo,
    selectedVenue,
  } = bookingSummary

  const pathToCsvFile = buildPathToBookingFile(
    isFilterByDigitalVenues,
    selectedOffer,
    selectOffersFrom,
    selectOffersTo,
    selectedVenue
  )

  const showButtons =
    !!(isFilterByDigitalVenues && selectedOffer) ||
    !!(selectedVenue && selectedOffer) ||
    selectedVenue === 'all'

  const showOfferSection = selectedVenue !== 'all' && (!!selectedVenue || !!isFilterByDigitalVenues)

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
