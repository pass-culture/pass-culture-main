import React from 'react'
import PropTypes from 'prop-types'

import { InputField } from '../../../../forms/inputs'
import withProfileForm from '../withProfileForm'

export const UserIdentifierField = props => {
  const { isLoading } = props

  return (
    <div className="pc-scroll-container">
      <div className="py30 px12 flex-1">
        <InputField
          disabled={isLoading}
          label="Votre identifiant"
          name="publicName"
          required
        />
      </div>
    </div>
  )
}

UserIdentifierField.propTypes = {
  isLoading: PropTypes.bool.isRequired,
}

export default withProfileForm(
  UserIdentifierField,
  {
    routeMethod: 'PATCH',
    routePath: 'users/current',
    stateKey: 'user',
  },
  null
)
