import React from 'react'
import PropTypes from 'prop-types'
import Siren from '../Fields/Siren/Siren'
import Name from '../Fields/Name'
import Address from '../Fields/Address'
import PostalCode from '../Fields/PostalCode'
import City from '../Fields/City'
import { NavLink } from 'react-router-dom'

function OffererCreationForm({ handleSubmit, invalid, pristine }) {
  return (
    <form onSubmit={handleSubmit}>
      <div className="section">
        <div className="field-group">
          <Siren />
          <Name />
          <Address />
          <PostalCode />
          <City />
        </div>
        <div
          className="offerer-form-validation"
          style={{ justifyContent: 'space-between' }}
        >
          <div className="control">
            <NavLink
              className="button is-secondary is-medium"
              to="/structures"
            >
              {'Retour'}
            </NavLink>
          </div>
          <div className="control">
            <button
              className="button is-primary is-medium"
              disabled={invalid || pristine}
              type="submit"
            >
              {'Valider'}
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
