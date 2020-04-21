import PropTypes from 'prop-types'
import React from 'react'

import TextField from '../../../../../layout/form/fields/TextField'

const BankFields = ({ adminUserOfferer, areBankInformationProvided, readOnly }) => {
  const areBankInfosReadOnly = readOnly || !adminUserOfferer

  return (
    <div className="section">
      <h2 className="main-list-title">
        {'Informations bancaires'}
        <span className="is-pulled-right fs13 has-text-grey">
          {!adminUserOfferer &&
            "Vous avez besoin d'être administrateur de la structure pour éditer ces informations."}
        </span>
      </h2>
      {!areBankInformationProvided && (
        <p className="bank-instructions-label fs13">
          {
            'Le pass Culture vous contactera prochainement afin d’enregistrer vos coordonnées bancaires. Une fois votre BIC / IBAN renseigné, ces informations apparaitront ci-dessous.'
          }
        </p>
      )}
      <div className="field-group">
        <TextField label="BIC : " name="bic" readOnly={areBankInfosReadOnly} />
        <TextField label="IBAN : " name="iban" readOnly={areBankInfosReadOnly} />
      </div>
    </div>
  )
}

BankFields.defaultProps = {
  adminUserOfferer: false,
  areBankInformationProvided: false,
  readOnly: true,
}

BankFields.propTypes = {
  adminUserOfferer: PropTypes.bool,
  areBankInformationProvided: PropTypes.bool,
  readOnly: PropTypes.bool,
}

export default BankFields
