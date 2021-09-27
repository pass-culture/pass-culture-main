/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 * @debt deprecated "Gaël: deprecated usage of react-final-form"
 * @debt deprecated "Gaël: deprecated usage of react-final-form custom fields"
 */

import React from 'react'
import { string } from 'yup'

import TextField from 'components/layout/form/fields/TextField'

const validatePhone = val => {
  const phoneRegex = /^(\+?\d{0,4})?\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{3}\)?)\s?-?\s?(\(?\d{4}\)?)?$/
  if (val && !phoneRegex.test(val)) {
    return 'Ce numéro de téléphone n’est pas valide merci de fournir un numéro de téléphone sans espaces'
  }
}

const validateEmail = async val => {
  const isValid = await string().email().isValid(val)
  if (!isValid) {
    return 'Votre email n’est pas valide'
  }
}

const validateUrl = async val => {
  const isValid = await string().url().isValid(val)
  if (!isValid) {
    return 'L’URL renseignée n’est pas valide'
  }
}

const ContactInfosFields = () => (
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
      placeholder="Ex : 06 06 06 06"
      type="phone"
      validate={validatePhone}
    />
    <TextField
      className="field text-field"
      label="Mail"
      name="contact.email"
      placeholder="Ex : nomprenom@nomdedomaine.fr"
      type="email"
      validate={validateEmail}
    />
    <TextField
      className="field text-field"
      label="URL de votre site web"
      name="contact.website"
      placeholder="https://votresite.com"
      type="url"
      validate={validateUrl}
    />
  </div>
)

export default ContactInfosFields
