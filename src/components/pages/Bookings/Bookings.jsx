import React from 'react'
import PropTypes from 'prop-types'

import DownloadButtonContainer from '../../layout/DownloadButton/DownloadButtonContainer'
import Main from '../../layout/Main'
import HeroSection from '../../layout/HeroSection/HeroSection'
import FilterByVenueContainer from './FilterByVenue/FilterByVenueContainer'
import DisplayButtonContainer from '../../layout/DisplayButton/DisplayButtonContainer'

const Bookings = ({pathToCsvFile, showButtons}) => (
  <Main name="bookings">
    <HeroSection title="Suivi des réservations">
      <p className="subtitle">
        {'Téléchargez le récapitulatif des réservations de vos offres.'}
        <br/>
        <br/>
        {'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.'}
      </p>
    </HeroSection>
    <hr/>
    <FilterByVenueContainer/>
    <div className="control flex-columns items-center flex-end">
      {showButtons && (
        <DownloadButtonContainer
          filename="reservations_pass_culture"
          href={pathToCsvFile}
          mimeType="text/csv"
        >
          {'Télécharger la liste des réservations'}
        </DownloadButtonContainer>
      )}
    </div>
    <br/>
    <div className="control flex-columns items-center flex-end">
      {showButtons && (
        <DisplayButtonContainer
          href={pathToCsvFile}
        >
          {'Afficher la liste des réservations'}
        </DisplayButtonContainer>
      )}
    </div>
  </Main>
)

Bookings.defaultProps = {
  pathToCsvFile: '',
  showButtons: false,
}

Bookings.propTypes = {
  pathToCsvFile: PropTypes.string,
  showButtons: PropTypes.bool,
}

export default Bookings
