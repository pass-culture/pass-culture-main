/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import { InputField } from '../../../forms/inputs'
import withProfileForm from './withProfileForm'

class ProfileIdentifiantForm extends React.PureComponent {
  render() {
    const { isLoading } = this.props
    return (
      <div className="pc-scroll-container">
        <div className="padded flex-1">
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

ProfileIdentifiantForm.propTypes = {
  isLoading: PropTypes.bool.isRequired,
}

export default withProfileForm(ProfileIdentifiantForm)
