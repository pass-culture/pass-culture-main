import PropTypes from 'prop-types'
import { DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL } from '../../../../../utils/config'
import React, { Fragment } from 'react'
import Icon from '../../../../layout/Icon'

const BankInformation = ({ venue, offerer }) => {
  const venueHasBankInformation = !!(venue.iban && venue.bic)

  const iban = venueHasBankInformation ? venue.iban : offerer.iban
  const bic = venueHasBankInformation ? venue.bic : offerer.bic

  const displayBankInformations = !!(bic && iban)
  const displayApplicationLink =
    !venueHasBankInformation && !!venue.demarchesSimplifieesApplicationId

  return (
    <div className="section vp-content-section bank-information">
      <h2 className="main-list-title">
        {'Coordonnées bancaires du lieu'}
      </h2>

      {displayBankInformations && (
        <Fragment>
          <a
            className="bi-external-link bi-external-link--mod-topright"
            href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon
              alt=""
              svg="ico-external-site"
            />
            {'Modifier'}
          </a>
          <p className="bi-subtitle">
            {
              'Les remboursements des offres éligibles présentées dans ce lieu sont effectués sur le compte ci-dessous :'
            }
          </p>
          <div className="vp-detail">
            <span>
              {'IBAN : '}
            </span>
            <span>
              {iban}
            </span>
          </div>
          <div className="vp-detail">
            <span>
              {'BIC : '}
            </span>
            <span>
              {bic}
            </span>
          </div>
        </Fragment>
      )}
      {displayApplicationLink && (
        <div className="bi-banner">
          <p>
            {'Votre dossier est en cours pour ce lieu'}
          </p>

          <p>
            <a
              className="bi-external-link"
              href={`https://www.demarches-simplifiees.fr/dossiers/${venue.demarchesSimplifieesApplicationId}`}
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon
                alt=""
                svg="ico-external-site"
              />
              {'Accéder au dossier'}
            </a>
          </p>
        </div>
      )}
      {!displayBankInformations && !displayApplicationLink && (
        <Fragment>
          <p className="bi-subtitle">
            {'Aucune coordonnée bancaire renseignée'}
          </p>
          <div className="bi-banner">
            <p>
              {
                'Renseignez vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles'
              }
            </p>

            <p>
              <a
                className="bi-external-link"
                href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
                rel="noopener noreferrer"
                target="_blank"
              >
                <Icon
                  alt=""
                  svg="ico-external-site"
                />
                {'Renseignez les coordonnées bancaires du lieu'}
              </a>
            </p>
          </div>
        </Fragment>
      )}
    </div>
  )
}

BankInformation.defaultProps = {
  venue: {},
}
BankInformation.propTypes = {
  offerer: PropTypes.shape().isRequired,
  venue: PropTypes.shape(),
}

export default BankInformation
