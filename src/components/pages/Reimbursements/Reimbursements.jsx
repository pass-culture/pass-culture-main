import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import CsvTableButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Main from 'components/layout/Main'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { API_URL } from 'utils/config'

const Reimbursements = () => (
  <Main name="reimbursements">
    <PageTitle title="Vos remboursements" />
    <Titles title="Remboursements" />
    <p className="advice">
      {'Téléchargez le récapitulatif des remboursements de vos offres.'}
    </p>
    <p className="advice">
      {'Le fichier est au format CSV, compatible avec tous les tableurs et éditeurs de texte.'}
    </p>
    <Banner
      href="https://aide.passculture.app/fr/article/acteurs-calendrier-des-prochains-remboursements-54t3e/"
      linkTitle="En savoir plus sur les prochains remboursements"
      type="notification-info"
    />
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
