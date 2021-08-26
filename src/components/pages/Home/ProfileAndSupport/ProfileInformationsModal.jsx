/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import TextInput from 'components/layout/inputs/TextInput/TextInput'
import * as pcapi from 'repository/pcapi/pcapi'

const ProfileInformationsModal = ({
  hideProfileInfoModal,
  setUserInformations,
  showSuccessNotification,
  user,
}) => {
  const [lastName, setLastName] = useState(user.lastName || '')
  const [firstName, setFirstName] = useState(user.firstName || '')
  const [email, setEmail] = useState(user.email || '')
  const [phoneNumber, setPhoneNumber] = useState(user.phoneNumber || '')
  const [formErrors, setFormErrors] = useState({})

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
          setUserInformations(user, body)
          showSuccessNotification()
          hideProfileInfoModal()
        })
        .catch(error => {
          setFormErrors(error.errors)
        })
    },
    [
      firstName,
      lastName,
      email,
      hideProfileInfoModal,
      phoneNumber,
      setUserInformations,
      showSuccessNotification,
      user,
    ]
  )

  const setInput = setter => event => setter(event.target.value)

  return (
    <DialogBox
      labelledBy="modal-profile"
      onDismiss={hideProfileInfoModal}
    >
      <div className="profile-info-modal">
        <h1
          className="pi-title"
          id="modal-profile"
        >
          Profil
        </h1>
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
            <button
              className="secondary-button"
              onClick={hideProfileInfoModal}
              type="button"
            >
              Annuler
            </button>
            <button
              className="primary-button"
              type="submit"
            >
              Enregistrer
            </button>
          </div>
        </form>
      </div>
    </DialogBox>
  )
}

ProfileInformationsModal.propTypes = {
  hideProfileInfoModal: PropTypes.func.isRequired,
  setUserInformations: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
  user: PropTypes.shape({
    firstName: PropTypes.string,
    lastName: PropTypes.string,
    email: PropTypes.string,
    phoneNumber: PropTypes.string,
  }).isRequired,
}

export default ProfileInformationsModal
