import { compose } from 'redux'
import { requestData } from 'redux-saga-data'
import { connect } from 'react-redux'
import withFrenchQueryRouter from '../../../hocs/withFrenchQueryRouter'

import FilterByVenue from './FilterByVenue'
import { closeNotification, showNotification } from 'pass-culture-shared'
import { selectIsUserAdmin } from '../../../../selectors/data/usersSelectors'

import { selectNonVirtualVenues } from '../../../../selectors/data/venuesSelectors'

export const mapDispatchToProps = dispatch => ({
  closeNotification: () => {
    dispatch(closeNotification())
  },
  loadVenues: () => {
    dispatch(
      requestData({
        apiPath: '/venues',
        stateKey: 'venues',
        method: 'GET',
      })
    )
  },
  showNotification: () => {
    dispatch(
      showNotification({
        tag: 'admin-bookings-access',
        text:
          'Votre statut d’administrateur ne permet pas de télécharger le suivi des réservations',
        type: 'info',
      })
    )
  },
  updateIsFilteredByDigitalVenues: payload => {
    dispatch({
      payload,
      type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES',
    })
  },
  updateVenueId: event => {
    dispatch({
      payload: event.target.value,
      type: 'BOOKING_SUMMARY_UPDATE_VENUE_ID',
    })
  },
})

export const mapStateToProps = state => {
  const { data = {} } = state
  const { venues } = data

  const { bookingSummary = {} } = state
  const { isFilteredByDigitalVenues, venueId } = bookingSummary

  const isUserAdmin = selectIsUserAdmin(state)

  const allVenuesOption = {
    name: 'Tous les lieux',
    id: 'all',
  }

  let venuesOptions = []
  if (!isUserAdmin) {
    const nonVirtualVenues = selectNonVirtualVenues(state, venues)
    venuesOptions = [allVenuesOption, ...nonVirtualVenues]
  }

  return {
    isDigital: isFilteredByDigitalVenues,
    isUserAdmin,
    notification: state.notification,
    venueId,
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
