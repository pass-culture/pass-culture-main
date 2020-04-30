import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { NavLink } from 'react-router-dom'
import { FormSpy } from 'react-final-form'
import SirenField from '../../../../layout/form/fields/SirenField/SirenField'

class OffererCreationForm extends Component {
  shouldComponentUpdate() {
    return true
  }

  renderAddress = ({ values }) => (
    <div className="op-detail-creation-form">
      <span>
        {'Siège social : '}
      </span>
      {values.postalCode && (
        <span>
          {`${values.address} - ${values.postalCode} ${values.city}`}
        </span>
      )}
    </div>
  )
  renderName = ({ values }) => (
    <div className="op-detail-creation-form">
      <span>
        {'Désignation : '}
      </span>
      {values.name &&
      <span>
        {values.name}
      </span>}
    </div>
  )

  render() {
    const { handleSubmit, invalid, pristine } = this.props
    return (
      <form onSubmit={handleSubmit}>
        <div className="section">
          <div className="op-creation-form">
            <SirenField />
            <FormSpy render={this.renderName} />
            <FormSpy render={this.renderAddress} />
          </div>
          <div className="offerer-form-validation">
            <div className="control">
              <NavLink
                className="button is-tertiary is-medium"
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
                {'Créer'}
              </button>
            </div>
          </div>
        </div>
      </form>
    )
  }
}

OffererCreationForm.propTypes = {
  handleSubmit: PropTypes.func.isRequired,
  invalid: PropTypes.bool.isRequired,
  pristine: PropTypes.bool.isRequired,
}

export default OffererCreationForm
