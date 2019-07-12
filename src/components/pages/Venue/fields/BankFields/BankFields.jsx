import PropTypes from 'prop-types'
import React from 'react'

import TextField from '../../../../layout/form/fields/TextField'

const BankFields = ({
  adminUserOfferer,
  readOnly,
}) => {
  const areBankInfosReadOnly = readOnly || !adminUserOfferer

  return (
    <div className="section">
      <h2 className="main-list-title">
        {"INFORMATIONS BANCAIRES"}
        <span className="is-pulled-right is-size-7 has-text-grey">
          {!adminUserOfferer &&
            "Vous avez besoin d'être administrateur de la structure pour éditer ces informations."}
        </span>
      </h2>
      <div className="field-group">
        <TextField
          label="BIC : "
          name="bic"
          readOnly={areBankInfosReadOnly}
        />
        <TextField
          label="IBAN : "
          name="iban"
          readOnly={areBankInfosReadOnly}
        />
      </div>
    </div>
  )
}

BankFields.defaultProps = {
  adminUserOfferer: false,
  readOnly: true,
}

BankFields.propTypes = {
  adminUserOfferer: PropTypes.bool,
  readOnly: PropTypes.bool,
}

export default BankFields
