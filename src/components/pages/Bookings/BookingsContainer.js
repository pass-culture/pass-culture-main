import { connect } from 'react-redux';
import { compose } from 'redux';
import { requestData } from 'redux-saga-data'

import Bookings from './Bookings'
import { withFrenchQueryRouter, withRedirectToSigninWhenNotAuthenticated } from 'components/hocs'


const mapDispatchToProps = (dispatch, ownProps) => ({
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
  const { shouldLoadVenue, shouldLoadOffers, venues, offers } = state.data

  const allVenues = {
    name: "Tous les lieux",
    id: "all",
  }
  venues.unshift(allVenues)

  const allOffers = {
    name: "Toutes les offres",
    id: "all",
  }
  offers.unshift(allOffers)

  console.log("allOffers",allOffers)

  /*
  const digitalOffers = selectDigitalOffers()
  console.log('digitalOffers', digitalOffers)
  */

  return {
    shouldLoadVenue,
    shouldLoadOffers,
    venues,
    offers
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

