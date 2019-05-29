import React from 'react'

import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Main from 'components/layout/Main'
import HeroSection from 'components/layout/HeroSection'
import { API_URL } from 'utils/config'

const Bookings = () => (
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
    <div className="control flex-columns items-center flex-end">
      <DownloadButtonContainer
        filename="reservations_pass_culture_pass_culture"
        href={`${API_URL}/bookings/csv`}
        mimeType="text/csv">
        Télécharger la liste des réservations
      </DownloadButtonContainer>
    </div>
  </Main>
)

export default Bookings
