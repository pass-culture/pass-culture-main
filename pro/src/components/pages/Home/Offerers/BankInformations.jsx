/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import Icon from 'components/layout/Icon'
import { DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

const BankInformations = ({
  offerer,
  hasMissingBankInformation,
  hasRejectedOrDraftOffererBankInformations,
}) => {
  return (
    <>
      <h3 className="h-card-secondary-title">
        Coordonnées bancaires
        {hasMissingBankInformation && (
          <Icon
            alt="Informations bancaires manquantes"
            className="ico-bank-warning"
            svg="ico-alert-filled"
          />
        )}
      </h3>

      <div className="h-card-content">
        {hasRejectedOrDraftOffererBankInformations ? (
          <Banner
            href={`https://www.demarches-simplifiees.fr/dossiers/${offerer.demarchesSimplifieesApplicationId}`}
            linkTitle="Voir le dossier"
          >
            Votre dossier est en cours pour cette structure
          </Banner>
        ) : (
          <Banner
            href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
            linkTitle="Renseignez les coordonnées bancaires"
          >
            Certains de vos lieux ne sont pas rattachés à des coordonnées bancaires. Pour percevoir
            les remboursements liés aux offres postées dans ces lieux, renseignez les coordonnées
            bancaires.
          </Banner>
        )}
      </div>
    </>
  )
}

BankInformations.propTypes = {
  hasMissingBankInformation: PropTypes.bool.isRequired,
  hasRejectedOrDraftOffererBankInformations: PropTypes.bool.isRequired,
  offerer: PropTypes.shape({
    iban: PropTypes.string,
    bic: PropTypes.string,
    demarchesSimplifieesApplicationId: PropTypes.string,
  }).isRequired,
}

export default BankInformations
