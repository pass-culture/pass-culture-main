import React from 'react'

import DownloadButtonContainer from '../../layout/DownloadButton/DownloadButtonContainer'
import Main from '../../layout/Main'
import HeroSection from '../../layout/HeroSection/HeroSection'
import { API_URL } from '../../../utils/config'

const Reimbursements = () => (
  <Main name="reimbursements">
    <HeroSection title="Suivi des remboursements">
      <p className="subtitle">{'Téléchargez le récapitulatif des remboursements de vos offres.'}</p>

      <p className="subtitle">
        {'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.'}
      </p>
    </HeroSection>
    <hr />
    <div className="control flex-columns items-center flex-end">
      <DownloadButtonContainer
        filename="remboursements_pass_culture"
        href={`${API_URL}/reimbursements/csv`}
        mimeType="text/csv"
      >
        {'Télécharger la liste des remboursements'}
      </DownloadButtonContainer>
    </div>
  </Main>
)

export default Reimbursements
