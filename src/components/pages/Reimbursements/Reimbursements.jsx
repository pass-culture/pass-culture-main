import React from 'react'

import AppLayout from 'app/AppLayout'
import Banner from 'components/layout/Banner/Banner'
import CsvTableButtonContainer from 'components/layout/CsvTableButton/CsvTableButtonContainer'
import DownloadButtonContainer from 'components/layout/DownloadButton/DownloadButtonContainer'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { API_URL } from 'utils/config'

const Reimbursements = () => (
  <AppLayout
    layoutConfig={{
      pageName: 'reimbursements',
    }}
  >
    <PageTitle title="Vos remboursements" />
    <Titles title="Remboursements" />
    <p>
      {
        'Les remboursements s’effectuent tous les 15 jours, rétroactivement suite à la validation d’une contremarque dans le guichet ou à la validation automatique des contremarques d’évènements. Cette page est automatiquement mise à jour à chaque remboursement.'
      }
    </p>
    <Banner type="notification-info">
      {'En savoir plus sur'}
      <a
        className="bi-link tertiary-link"
        href="https://aide.passculture.app/fr/articles/5096833-acteurs-culturels-quel-est-le-calendrier-des-prochains-remboursements"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        {'Les prochains remboursements'}
      </a>
      <a
        className="bi-link tertiary-link"
        href="https://aide.passculture.app/fr/articles/5096171-acteurs-culturels-comment-determiner-ses-modalites-de-remboursement"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site" />
        {'Les modalités de remboursement'}
      </a>
    </Banner>
    <p>
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
  </AppLayout>
)

export default Reimbursements
