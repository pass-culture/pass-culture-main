import * as pcapi from 'repository/pcapi/pcapi'

import React, { useCallback, useState } from 'react'

import PropTypes from 'prop-types'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import { setCurrentUser } from 'store/user/actions'
import { useDispatch } from 'react-redux'
import useNotification from 'components/hooks/useNotification'

const ProfileForm = ({ onCancel, onSuccess, initialValues }) => {
  const [lastName, setLastName] = useState(initialValues.lastName || '')
  const [firstName, setFirstName] = useState(initialValues.firstName || '')
  const [email, setEmail] = useState(initialValues.email || '')
  const [phoneNumber, setPhoneNumber] = useState(
    initialValues.phoneNumber || ''
  )
  const [formErrors, setFormErrors] = useState({})

  const notification = useNotification()
  const dispatch = useDispatch()

  const submitProfileInformations = useCallback(
    event => {
      event.preventDefault()
      const body = {
        firstName: firstName,
        lastName: lastName,
        email: email,
        phoneNumber: phoneNumber,
      }

      pcapi
        .updateUserInformations(body)
        .then(() => {
          dispatch(setCurrentUser(body))
          notification.success('Les informations ont bien été enregistrées.')
          onSuccess()
        })
        .catch(error => {
          'errors' in error && setFormErrors(error.errors)
        })
    },
    [dispatch, firstName, lastName, email, notification, onSuccess, phoneNumber]
  )

  const setInput = setter => event => setter(event.target.value)

  return (
    <>
      <div className="pi-mandatory-message">
        Tous les champs sont obligatoires
      </div>
      <form onSubmit={submitProfileInformations}>
        <TextInput
          error={formErrors.lastName?.[0]}
          label="Nom"
          name="last-name-input"
          onChange={setInput(setLastName)}
          value={lastName}
        />
        <TextInput
          error={formErrors.firstName?.[0]}
          label="Prénom"
          name="first-name-input"
          onChange={setInput(setFirstName)}
          value={firstName}
        />
        <TextInput
          error={formErrors.email?.[0]}
          label="Email"
          name="email-input"
          onChange={setInput(setEmail)}
          value={email}
        />
        <TextInput
          error={formErrors.phoneNumber?.[0]}
          label="Téléphone"
          name="phone-input"
          onChange={setInput(setPhoneNumber)}
          value={phoneNumber}
        />
        <div className="actions-group">
          <button className="secondary-button" onClick={onCancel} type="button">
            Annuler
          </button>
          <button className="primary-button" type="submit">
            Enregistrer
          </button>
        </div>
      </form>
    </>
  )
}

ProfileForm.defaultProps = {
  initialValues: PropTypes.shape({
    firstName: '',
    lastName: '',
    email: '',
    phoneNumber: '',
  }),
}

ProfileForm.propTypes = {
  initialValues: PropTypes.shape({
    firstName: PropTypes.string,
    lastName: PropTypes.string,
    email: PropTypes.string,
    phoneNumber: PropTypes.string,
  }),
  onCancel: PropTypes.func.isRequired,
  onSuccess: PropTypes.func.isRequired,
}

export default ProfileForm
