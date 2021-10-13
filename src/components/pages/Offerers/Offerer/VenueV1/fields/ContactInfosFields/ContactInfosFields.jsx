/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 * @debt deprecated "Gaël: deprecated usage of react-final-form"
 * @debt deprecated "Gaël: deprecated usage of react-final-form custom fields"
 */

import PropTypes from 'prop-types'
import React from 'react'

import TextField from 'components/layout/form/fields/TextField'

import { validatePhone, validateEmail, validateUrl } from './validators'

const ContactInfosFields = ({ readOnly }) => (
  <div className="section vp-content-section bank-information">
    <div className="main-list-title title-actions-container">
      <h2 className="main-list-title-text">
        Contact
      </h2>
    </div>

    <TextField
      className="field text-field"
      label="Téléphone"
      name="contact.phoneNumber"
      readOnly={readOnly}
      type="phone"
      validate={validatePhone}
    />
    <TextField
      className="field text-field"
      label="Mail"
      name="contact.email"
      readOnly={readOnly}
      type="email"
      validate={validateEmail}
    />
    <TextField
      className="field text-field"
      label="URL de votre site web"
      name="contact.website"
      readOnly={readOnly}
      type="url"
      validate={validateUrl}
    />
  </div>
)

ContactInfosFields.propTypes = {
  readOnly: PropTypes.bool.isRequired,
}

export default ContactInfosFields
