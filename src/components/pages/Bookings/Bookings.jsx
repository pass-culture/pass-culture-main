import React, { Component } from 'react'
import PropTypes from 'prop-types'

import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Main from 'components/layout/Main'
import HeroSection from 'components/layout/HeroSection/HeroSection'
import { API_URL } from 'utils/config'
import FilterByVenueContainer from './FilterByVenueContainer'
import FilterByOfferContainer from './FilterByOfferContainer'
import {FilterByVenue} from "./FilterByVenue";

class Bookings extends Component {
  render() {
    const { isFilterByDigitalVenues, selectedOffer, selectedVenue } = this.props

    let showDownloadButtonContainer = true
    if (
      (!isFilterByDigitalVenues && selectedVenue === '') ||
      selectedOffer === ''
    ) {
      showDownloadButtonContainer = false
    }

    return (
      <Main name="bookings">
        <HeroSection title="Suivi des réservations">
          <p className="subtitle">
            Téléchargez le récapitulatif des réservations de vos offres.
          </p>

          <p className="subtitle">
            Le fichier est au format CSV, compatible avec tous les tableurs et
            éditeurs de texte.
          </p>
        </HeroSection>
        <hr />
        <FilterByVenueContainer />
        <FilterByOfferContainer />
        <div className="control flex-columns items-center flex-end">
          {showDownloadButtonContainer ? (
            <DownloadButtonContainer
              filename="reservations_pass_culture"
              href={`${API_URL}/bookings/csv`}
              mimeType="text/csv">
              Télécharger la liste des réservations
            </DownloadButtonContainer>
          ) : null}
        </div>
      </Main>
    )
  }
}

FilterByVenue.defaultProps = {
  isFilterByDigitalVenues: false,
  selectedOffer: '',
  selectedVenue:'',
}

Bookings.propTypes = {
  isFilterByDigitalVenues: PropTypes.bool,
  selectedOffer: PropTypes.string,
  selectedVenue: PropTypes.string,
}

export default Bookings
