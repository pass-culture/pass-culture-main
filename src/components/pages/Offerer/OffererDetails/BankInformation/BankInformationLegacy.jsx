import React, { Fragment } from 'react'
import { Offerer } from '../Offerer'
import PropTypes from 'prop-types'

const BankInformationLegacy = ({ offerer }) => (
  <Fragment>
    <div className="section">
      <h2 className="main-list-title">
        {'Informations bancaires'}
        <span className="is-pulled-right is-size-7 has-text-grey">
          {!offerer.adminUserOfferer &&
            "Vous avez besoin d'être administrateur de la structure pour modifier ces informations."}
        </span>
      </h2>
      {!offerer.areBankInformationProvided && (
        <p className="bank-instructions-label">
          {
            'Le pass Culture vous contactera prochainement afin d’enregistrer vos coordonnées bancaires. Une fois votre BIC / IBAN renseigné, ces informations apparaitront ci-dessous.'
          }
        </p>
      )}
    </div>
    <div>
      <div>
        <label>
          {'BIC : '}
        </label>
        <span>
          {offerer.bic}
        </span>
      </div>
      <div>
        <label>
          {'IBAN : '}
        </label>
        <span>
          {offerer.iban}
        </span>
      </div>
    </div>
  </Fragment>
)

BankInformationLegacy.propTypes = {
  offerer: PropTypes.instanceOf(Offerer).isRequired,
}

export default BankInformationLegacy
