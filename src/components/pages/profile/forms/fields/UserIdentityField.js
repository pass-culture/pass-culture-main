import React from 'react'
import PropTypes from 'prop-types'

import { InputField } from '../../../../forms/inputs'
import withProfileForm from '../withProfileForm'

// FIXME: ce composant n'a pas l'air utilisé. Faut-il le conserver ?
export class UserIdentityField extends React.PureComponent {
  render() {
    const { isLoading } = this.props
    return (
      <div className="pc-scroll-container">
        <div className="py30 px12 flex-1">
          <InputField
            required
            name="lastName"
            label="Votre nom"
            disabled={isLoading}
            placeholder="Saisissez votre nom"
          />
          <InputField
            required
            name="firstName"
            className="mt36"
            label="Votre prénom"
            disabled={isLoading}
            placeholder="Saisissez votre prénom"
          />
        </div>
      </div>
    )
  }
}

UserIdentityField.propTypes = {
  isLoading: PropTypes.bool.isRequired,
}

export default withProfileForm(
  UserIdentityField,
  {
    routeMethod: 'PATCH',
    routePath: 'users/current',
    stateKey: 'user',
  },
  null
)
