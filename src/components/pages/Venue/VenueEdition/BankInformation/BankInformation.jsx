import PropTypes from 'prop-types'
import { DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL } from '../../../../../utils/config'
import React, { Fragment } from 'react'
import Icon from '../../../../layout/Icon'

const BankInformation = ({ venue, offerer }) => {
  const venueBankInformation = venue.iban && venue.bic
  const iban = venueBankInformation ? venue.iban : offerer.iban
  const bic = venueBankInformation ? venue.bic : offerer.bic

  return (
    <div className="section op-content-section bank-information">
      <h2 className="main-list-title">{'Coordonnées bancaires du lieu'}</h2>

      {bic && iban ? (
        <Fragment>
          <a
            className="bi-external-link bi-external-link--mod-topright"
            href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon alt="" svg="ico-external-site" />
            {'Modifier'}
          </a>
          <p className="bi-subtitle">
            {
              'Les remboursements des offres éligibles présentées dans ce lieu sont effectués sur le compte ci-dessous :'
            }
          </p>
          <div className="op-detail">
            <span>{'IBAN : '}</span>
            <span>{iban}</span>
          </div>
          <div className="op-detail">
            <span>{'BIC : '}</span>
            <span>{bic}</span>
          </div>
        </Fragment>
      ) : (
        <Fragment>
          <p className="bi-subtitle">{'Aucune coordonnée bancaire renseignée'}</p>
          <div className="bi-banner">
            <p>
              {
                'Renseigner vos coordonnées bancaires pour ce lieu pour être remboursé de vos offres éligibles'
              }
            </p>

            <p>
              <a
                className="bi-external-link"
                href={DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL}
                rel="noopener noreferrer"
                target="_blank"
              >
                <Icon alt="" svg="ico-external-site" />
                {'Renseigner les coordonnées bancaires du lieu'}
              </a>
            </p>
          </div>
        </Fragment>
      )}
    </div>
  )
}

BankInformation.propTypes = {
  offerer: PropTypes.shape().isRequired,
  venue: PropTypes.shape().isRequired,
}

export default BankInformation
