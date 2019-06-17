import { connect } from 'react-redux';
import { compose } from 'redux';
import { requestData } from 'redux-saga-data'

import Bookings from './Bookings'
import { withFrenchQueryRouter, withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'
import selectNonVirtualVenues from './selectNonVirtualVenues'
import selectDigitalOffers from './selectDigitalOffers'

const mapDispatchToProps = (dispatch) => ({
  loadVenues: () => {
    dispatch(requestData({
      apiPath: `/venues`,
      stateKey: 'venues',
      method: 'GET'
    }))
  },
  loadOffers: () => {
    dispatch(requestData({
      apiPath: `/offers`,
      stateKey: 'offers',
      method: 'GET'
    }))
  }
})

const mapStateToProps = state => {
  const { venues, offers } = state.data

  const allVenuesOption = {
    name: "Tous les lieux",
    id: "all",
  }

  const nonVirtualVenues = selectNonVirtualVenues(state, venues)
  const venuesOptions = [allVenuesOption, ...nonVirtualVenues]

  const allOffersOption = {
    name: "Toutes les offres",
    id: "all",
  }
  const digitalOffers = selectDigitalOffers(state, offers)
  const digitalOffersOptions = [allOffersOption, ...digitalOffers]

  return {
    venuesOptions,
    digitalOffersOptions
  }
}

export default compose(
  withRedirectToSigninWhenNotAuthenticated,
  withFrenchQueryRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Bookings)

