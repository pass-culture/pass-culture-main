import React from 'react'

import DownloadButton from 'components/layout/DownloadButton'
import Main from 'components/layout/Main'
import HeroSection from 'components/layout/HeroSection'
import { API_URL } from 'utils/config'

const Reimbursements = () => (
  <Main name="reimbursements">
    <HeroSection title="Suivi des remboursements">
      <p className="subtitle">
        Téléchargez le récapitulatif des remboursements de vos offres.
      </p>

      <p className="subtitle">
        Le fichier est au format CSV, compatible avec tous les tableurs et
        éditeurs de texte.
      </p>
    </HeroSection>
    <hr />
    <div className="control flex-columns items-center flex-end">
      <DownloadButton fileType="text/csv" href={`${API_URL}/booking_csv`}>
        Télécharger la liste des remboursements
      </DownloadButton>
    </div>
  </Main>
)

export default Reimbursements
