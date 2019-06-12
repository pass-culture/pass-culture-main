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
  const { venues, offers } = state.data

  const allVenuesOption = {
    name: "Tous les lieux",
    id: "all",
  }
  const venuesOptions = [allVenuesOption, ...venues]

  const allOffersOption = {
    name: "Toutes les offres",
    id: "all",
  }
  const offersOptions = [allOffersOption, ...offers]

  // TO DO : sortir du container et mettre dans un selector
  // mettre les selector dans le même dossier

  /*
  const digitalOffers = selectDigitalOffers()
  console.log('digitalOffers', digitalOffers)
  */

  return {
    venuesOptions,
    offersOptions
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

