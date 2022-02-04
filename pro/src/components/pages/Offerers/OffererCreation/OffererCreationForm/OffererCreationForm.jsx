import PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import { FormSpy } from 'react-final-form'
import { Link } from 'react-router-dom'

import SirenField from 'components/layout/form/fields/SirenField/SirenField'

const OffererCreationForm = ({ backTo, handleSubmit, invalid, pristine }) => {
  const renderAddress = useCallback(
    ({ values }) => (
      <div className="op-detail-creation-form">
        <span>{'Siège social : '}</span>
        {values.postalCode && (
          <span>
            {`${values.address} - ${values.postalCode} ${values.city}`}
          </span>
        )}
      </div>
    ),
    []
  )
  const renderName = useCallback(
    ({ values }) => (
      <div className="op-detail-creation-form">
        <span>{'Désignation : '}</span>
        {values.name && <span>{values.name}</span>}
      </div>
    ),
    []
  )

  return (
    <form onSubmit={handleSubmit}>
      <div className="section">
        <div className="op-creation-form">
          <SirenField />
          <FormSpy render={renderName} />
          <FormSpy render={renderAddress} />
        </div>
        <div className="offerer-form-validation">
          <div className="control">
            <Link className="secondary-link" to={backTo}>
              Retour
            </Link>
          </div>
          <div className="control">
            <button
              className="primary-button"
              disabled={invalid || pristine}
              type="submit"
            >
              Créer
            </button>
          </div>
        </div>
      </div>
    </form>
  )
}

OffererCreationForm.propTypes = {
  backTo: PropTypes.string.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  invalid: PropTypes.bool.isRequired,
  pristine: PropTypes.bool.isRequired,
}

export default OffererCreationForm
