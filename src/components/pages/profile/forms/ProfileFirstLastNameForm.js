/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { InputField } from '../../../forms/inputs'
import withProfileForm from './withProfileForm'

const initialValues = {
  firstName: null,
  lastName: null,
}

class ProfileFirstLastNameForm extends React.PureComponent {
  render() {
    const { isLoading } = this.props
    return (
      <div className="pc-scroll-container">
        <div className="padded flex-1">
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

ProfileFirstLastNameForm.propTypes = {
  isLoading: PropTypes.bool.isRequired,
}

export default withProfileForm(
  ProfileFirstLastNameForm,
  null,
  // TODO -> plutot les options de route par un objet
  'users/current',
  'PATCH',
  'user',
  initialValues
)
