import React from 'react'
import PropTypes from 'prop-types'
import Siren from '../Fields/Siren/Siren'
import { NavLink } from 'react-router-dom'
import { FormSpy } from 'react-final-form'

function OffererCreationForm({ handleSubmit, invalid, pristine }) {
  return (
    <form onSubmit={handleSubmit}>
      <div className="section">
        <div className="op-creation-form">
          <Siren />
          <FormSpy
            render={({ values }) => (
              <div className="op-detail op-creation-form-detail">
                <span>{'Désignation : '}</span>
                {values.name && <span>{values.name}</span>}
              </div>
            )}
          />
          <FormSpy
            render={({ values }) => (
              <div className="op-detail op-creation-form-detail">
                <span>{'Siège social : '}</span>
                {values.postalCode && (
                  <span>{`${values.address} - ${values.postalCode} ${values.city}`}</span>
                )}
              </div>
            )}
          />
        </div>
        <div className="offerer-form-validation" style={{ justifyContent: 'space-between' }}>
          <div className="control">
            <NavLink className="button is-secondary is-medium" to="/structures">
              {'Retour'}
            </NavLink>
          </div>
          <div className="control">
            <button
              className="button is-primary is-medium"
              disabled={invalid || pristine}
              type="submit"
            >
              {'Créer'}
            </button>
          </div>
        </div>
      </div>
    </form>
  )
}

OffererCreationForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  invalid: PropTypes.bool.isRequired,
  pristine: PropTypes.bool.isRequired,
}

export default OffererCreationForm
