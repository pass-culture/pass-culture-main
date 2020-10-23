import React from 'react'

import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Main from 'components/layout/Main'
import Titles from 'components/layout/Titles/Titles'
import { API_URL } from 'utils/config'
import CsvTableButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'

const Reimbursements = () => (
  <Main name="reimbursements">
    <Titles title="Remboursements" />
    <p className="advice">
      {'Téléchargez le récapitulatif des remboursements de vos offres.'}
    </p>
    <p className="advice">
      {'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.'}
    </p>
    <hr />
    <div className="flex-end">
      <DownloadButtonContainer
        filename="remboursements_pass_culture"
        href={`${API_URL}/reimbursements/csv`}
        mimeType="text/csv"
      >
        {'Télécharger la liste des remboursements'}
      </DownloadButtonContainer>
      <CsvTableButtonContainer href={`${API_URL}/reimbursements/csv`}>
        {'Afficher la liste des remboursements'}
      </CsvTableButtonContainer>
    </div>
  </Main>
)

export default Reimbursements
