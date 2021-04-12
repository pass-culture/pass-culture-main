import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner/Banner'
import Icon from 'components/layout/Icon'
import { DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

const BankInformations = ({ offerer, hasMissingBankInformations }) => {
  return (
    <>
      <h3 className="h-card-secondary-title">
        {'Coordonnées bancaires'}
        {hasMissingBankInformations && (
          <Icon
            alt="Informations bancaires manquantes"
            className="ico-bank-warning"
            svg="ico-alert-filled"
          />
        )}
      </h3>

      <div className="h-card-content">
        {offerer.iban && offerer.bic ? (
          <>
            <p>
              {
                'Les coordonnées bancaires ci-dessous seront attribuées à tous les lieux sans coordonnées bancaires propres.'
              }
            </p>
            <ul className="h-description-list">
              <li className="h-dl-row">
                <span className="h-dl-title">
                  {'IBAN :'}
                </span>
                <span className="h-dl-description">
                  {offerer.iban}
                </span>
              </li>

              <li className="h-dl-row">
                <span className="h-dl-title">
                  {'BIC :'}
                </span>
                <span className="h-dl-description">
                  {offerer.bic}
                </span>
              </li>
            </ul>
          </>
        ) : offerer.demarchesSimplifieesApplicationId ? (
          <Banner
            href={`https://www.demarches-simplifiees.fr/dossiers/${offerer.demarchesSimplifieesApplicationId}`}
            linkTitle="Voir le dossier"
          >
            {'Votre dossier est en cours pour cette structure'}
          </Banner>
        ) : (
          <Banner
            href={DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL}
            linkTitle="Renseignez les coordonnées bancaires de la structure"
          >
            {'Renseignez vos coordonnées bancaires pour être remboursé de vos offres éligibles'}
          </Banner>
        )}
      </div>
    </>
  )
}

BankInformations.propTypes = {
  hasMissingBankInformations: PropTypes.bool.isRequired,
  offerer: PropTypes.shape({
    iban: PropTypes.string,
    bic: PropTypes.string,
    demarchesSimplifieesApplicationId: PropTypes.string,
  }).isRequired,
}

export default BankInformations
