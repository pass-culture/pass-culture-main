import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import Icon from 'components/layout/Icon'
import InvalidBusinessUnits from 'components/pages/Home/Offerers/InvalidBusinessUnits'
import { Banner } from 'ui-kit'
import { DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL } from 'utils/config'

import { Offerer } from '../Offerer'

const BankInformation = ({ offerer, hasBusinessUnitError }) => (
  <div className="section op-content-section bank-information">
    <div className="main-list-title title-actions-container">
      <h2 className="main-list-title-text">
        Coordonnées bancaires de la structure
      </h2>

      {offerer.areBankInformationProvided && (
        <a
          className="tertiary-link"
          href={DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL}
          rel="noopener noreferrer"
          target="_blank"
        >
          <Icon alt="lien externe, nouvel onglet" svg="ico-external-site" />
          Modifier
        </a>
      )}
    </div>

    {offerer.areBankInformationProvided ? (
      <Fragment>
        <p className="bi-subtitle">
          Les coordonnées bancaires ci-dessous seront attribuées à tous les
          lieux sans coordonnées bancaires propres :
        </p>
        <div className="op-detail">
          <span>{'IBAN : '}</span>
          <span>{offerer.iban}</span>
        </div>
        <div className="op-detail">
          <span>{'BIC : '}</span>
          <span>{offerer.bic}</span>
        </div>
      </Fragment>
    ) : (
      offerer.demarchesSimplifieesApplicationId && (
        <Banner
          href={`https://www.demarches-simplifiees.fr/dossiers/${offerer.demarchesSimplifieesApplicationId}`}
          linkTitle="Accéder au dossier"
        >
          Votre dossier est en cours pour cette structure
        </Banner>
      )
    )}
    {hasBusinessUnitError && (
      <InvalidBusinessUnits hasTitle={false} offererId={offerer.id} />
    )}
    <Banner
      href="https://passculture.zendesk.com/hc/fr/articles/4411992051601"
      linkTitle="En savoir plus sur les remboursements"
      type="notification-info"
    />
  </div>
)
BankInformation.defaultProps = {
  hasBusinessUnitError: false,
}
BankInformation.propTypes = {
  hasBusinessUnitError: PropTypes.bool,
  offerer: PropTypes.instanceOf(Offerer).isRequired,
}

export default BankInformation
