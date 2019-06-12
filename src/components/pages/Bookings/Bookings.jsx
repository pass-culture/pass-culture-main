import React, {Component} from 'react'
import PropTypes from 'prop-types'

import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Main from 'components/layout/Main'
import HeroSection from 'components/layout/HeroSection/HeroSection'
import { API_URL } from 'utils/config'
import {FilterByVenue} from './FilterByVenue'
import {FilterByOffer} from './FilterByOffer'
import {FilterByDigitalOffer} from './FilterByDigitalOffer'
import {FilterByDate} from './FilterByDate'

class Bookings extends Component {
  componentDidMount() {
    this.props.loadVenues()
    this.props.loadOffers()
  }

  render () {
    const {venuesOptions} = this.props
    const {offersOptions} = this.props

    return(
      <Main name="Bookings">
        <HeroSection title="Suivi des réservations">
          <p className="subtitle">
            Téléchargez le récapitulatif des réservations de vos offres.
          </p>

          <p className="subtitle">
            Le fichier est au format CSV, compatible avec tous les tableurs et
            éditeurs de texte.
          </p>
        </HeroSection>
        <hr/>
        <FilterByVenue
          venuesOptions={venuesOptions}
        />
        <SelectDigitalOffer
          filterState={this.state}
        />
        <FilterByOffer
          offers={offersOptions}
        />
        <FilterByDigitalOffer
          offers={offersOptions}
        />
        <FilterByDate
        />
        <div className="control flex-columns items-center flex-end">
          <DownloadButtonContainer
            filename="remboursements_pass_culture"
            href={`${API_URL}/Bookings/csv`}
            mimeType="text/csv">
            Télécharger la liste des remboursements
          </DownloadButtonContainer>
        </div>
      </Main>
    )
  }
}

Bookings.defaultProps = {
  venuesOptions: [],
  offersOptions: [],
}

Bookings.propTypes = {
  venuesOptions: PropTypes.array.isRequired,
  offersOptions: PropTypes.array.isRequired,
  loadVenues: PropTypes.func.isRequired,
  loadOffers: PropTypes.func.isRequired
}

export default Bookings
