import PropTypes from 'prop-types'
import React from 'react'

import { TextField } from 'components/layout/form/fields'

const BankFields = ({
  adminUserOfferer,
  initialIban,
  initialThumbCount,
  readOnly,
}) => {
  const areBankInfosReadOnly = readOnly || !adminUserOfferer

  const hasAlreadyRibUploaded = initialIban && initialThumbCount

  return (
    <div className="section">
      <h2 className="main-list-title">
        INFORMATIONS BANCAIRES
        <span className="is-pulled-right is-size-7 has-text-grey">
          {!adminUserOfferer &&
            "Vous avez besoin d'être administrateur de la structure pour editer ces informations."}
        </span>
      </h2>
      <div className="field-group">
        <TextField label="BIC : " name="bic" readOnly={areBankInfosReadOnly} />
        <TextField
          label="IBAN : "
          name="iban"
          readOnly={areBankInfosReadOnly}
        />
        {false && (
          <TextField
            label="Justificatif"
            name="rib"
            readOnly={readOnly || areBankInfosReadOnly}
            uploaded={hasAlreadyRibUploaded}
            type="file"
          />
        )}
      </div>
    </div>
  )
}

BankFields.defaultProps = {
  initialIban: null,
  initialThumbCount: null,
  readOnly: true,
}

BankFields.propTypes = {
  initialIban: PropTypes.string,
  initialThumbCount: PropTypes.number,
  readOnly: PropTypes.bool,
}

export default BankFields
