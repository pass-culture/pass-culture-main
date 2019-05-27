import React from 'react'
import PropTypes from 'prop-types'

import { InputField } from '../../../../forms/inputs'
import withProfileForm from '../withProfileForm'

const initialValues = {
  publicName: null,
}

class IdentifiantForm extends React.PureComponent {
  render() {
    const { isLoading } = this.props
    return (
      <div className="pc-scroll-container">
        <div className="py30 px12 flex-1">
          <InputField
            required
            name="publicName"
            label="Votre identifiant"
            disabled={isLoading}
          />
        </div>
      </div>
    )
  }
}

IdentifiantForm.propTypes = {
  isLoading: PropTypes.bool.isRequired,
}

export default withProfileForm(
  IdentifiantForm,
  {
    routeMethod: 'PATCH',
    routePath: 'users/current',
    stateKey: 'user',
  },
  initialValues,
  null
)
