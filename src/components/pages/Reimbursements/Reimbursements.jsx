import React from 'react'

import DownloadButtonContainer from '../../layout/DownloadButton/DownloadButtonContainer'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import { API_URL } from '../../../utils/config'
import CsvTableButtonContainer from '../../layout/CsvTableButton/CsvTableButtonContainer'

const Reimbursements = () => (
  <Main name="reimbursements">
    <Titles title="Suivi des remboursements" />
    <p className="advice">
      {'Téléchargez le récapitulatif des remboursements de vos offres.'}
    </p>
    <p className="advice">
      {'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.'}
    </p>
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
    <br />
    <div className="control flex-columns items-center flex-end">
      <CsvTableButtonContainer href={`${API_URL}/reimbursements/csv`}>
        {'Afficher la liste des remboursements'}
      </CsvTableButtonContainer>
    </div>
  </Main>
)

export default Reimbursements
