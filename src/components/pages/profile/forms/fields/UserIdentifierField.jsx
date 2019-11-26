import React from 'react'
import PropTypes from 'prop-types'

import InputField from '../../../../forms/inputs/InputField'
import withProfileForm from '../hocs/withProfileForm'

export const UserIdentifierField = ({ isLoading }) => (
  <InputField
    disabled={isLoading}
    label="Votre identifiant"
    name="publicName"
    required
  />
)

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
