import { Offerer } from '../Offerer'
import PropTypes from 'prop-types'
import { DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL } from '../../../../../utils/config'
import React, { Fragment } from 'react'
import Icon from '../../../../layout/Icon'

const BankInformation = ({ offerer }) => (
  <div className="section op-content-section bank-information">
    <h2 className="main-list-title">
      {'Coordonnées bancaires de la structure'}
    </h2>

    {offerer.areBankInformationProvided ? (
      <Fragment>
        <a
          className="bi-external-link bi-external-link--mod-topright"
          href={DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL}
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
            'Les coordonnées bancaires ci-dessous seront attribuées à tous les lieux sans coordonnées bancaires propres :'
          }
        </p>
        <div className="op-detail">
          <span>
            {'IBAN : '}
          </span>
          <span>
            {offerer.iban}
          </span>
        </div>
        <div className="op-detail">
          <span>
            {'BIC : '}
          </span>
          <span>
            {offerer.bic}
          </span>
        </div>
      </Fragment>
    ) : offerer.demarchesSimplifieesApplicationId ? (
      <div className="bi-banner">
        <p>
          {'Votre dossier est en cours pour cette structure'}
        </p>

        <p>
          <a
            className="bi-external-link"
            href={`https://www.demarches-simplifiees.fr/dossiers/${offerer.demarchesSimplifieesApplicationId}`}
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
    ) : (
      <Fragment>
        <p className="bi-subtitle">
          {'Aucune coordonnée bancaire renseignée'}
        </p>
        <div className="bi-banner">
          <p>
            {'Renseignez vos coordonnées bancaires pour être remboursé de vos offres éligibles'}
          </p>

          <p>
            <a
              className="bi-external-link"
              href={DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL}
              rel="noopener noreferrer"
              target="_blank"
            >
              <Icon
                alt=""
                svg="ico-external-site"
              />
              {'Renseignez les coordonnées bancaires de la structure'}
            </a>
          </p>
        </div>
      </Fragment>
    )}
  </div>
)

BankInformation.propTypes = {
  offerer: PropTypes.instanceOf(Offerer).isRequired,
}

export default BankInformation
