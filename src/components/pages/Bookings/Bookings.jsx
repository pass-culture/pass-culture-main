import React, { Component } from 'react'
import PropTypes from 'prop-types'

import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Main from 'components/layout/Main'
import HeroSection from 'components/layout/HeroSection/HeroSection'
import FilterByVenueContainer from './FilterByVenueContainer'

class Bookings extends Component {
  render() {
    const { pathToCsvFile, showDownloadButton } = this.props

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
        <div className="control flex-columns items-center flex-end">
          {showDownloadButton ? (
            <DownloadButtonContainer
              filename="reservations_pass_culture"
              href={pathToCsvFile}
              mimeType="text/csv">
              Télécharger la liste des réservations
            </DownloadButtonContainer>
          ) : null}
        </div>
      </Main>
    )
  }
}

Bookings.defaultProps = {
  pathToCsvFile: '',
  showDownloadButton: false,
}

Bookings.propTypes = {
  pathToCsvFile: PropTypes.string,
  showDownloadButton: PropTypes.bool,
}

export default Bookings
