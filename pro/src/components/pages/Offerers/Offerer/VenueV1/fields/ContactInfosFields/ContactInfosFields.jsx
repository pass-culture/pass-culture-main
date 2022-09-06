import PropTypes from 'prop-types'
import React from 'react'

import TextField from 'components/layout/form/fields/TextField'

import { validateEmail, validatePhone, validateUrl } from './validators'

const ContactInfosFields = ({ readOnly }) => (
  <div className="section vp-content-section bank-information">
    <div className="main-list-title title-actions-container">
      <h2 className="main-list-title-text">Contact</h2>
    </div>
    <p className="bi-subtitle">
      Ces informations seront affichées dans votre page lieu, sur l’application
      pass Culture. Elles permettront aux bénéficiaires de vous contacter en cas
      de besoin.
    </p>

    <TextField
      className="field text-field"
      label="Téléphone :"
      name="contact.phoneNumber"
      placeholder="0612345678"
      readOnly={readOnly}
      type="phone"
      validate={validatePhone}
    />
    <TextField
      className="field text-field"
      label="Mail :"
      name="contact.email"
      placeholder="email@exemple.com"
      readOnly={readOnly}
      type="email"
      validate={validateEmail}
    />
    <TextField
      className="field text-field"
      label="URL de votre site web :"
      name="contact.website"
      placeholder="http://exemple.com"
      readOnly={readOnly}
      type="text"
      validate={validateUrl}
    />
  </div>
)

ContactInfosFields.propTypes = {
  readOnly: PropTypes.bool.isRequired,
}

export default ContactInfosFields
