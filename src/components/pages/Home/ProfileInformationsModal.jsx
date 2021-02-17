import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import * as pcapi from '../../../repository/pcapi/pcapi'
import { DialogBox } from '../../layout/DialogBox/DialogBox'
import TextInput from '../../layout/inputs/TextInput/TextInput'

const ProfileInformationsModal = ({
  setIsModalOpened,
  setUserInformations,
  showSuccessNotification,
  user,
}) => {
  const [lastName, setLastName] = useState(user.lastName)
  const [firstName, setFirstName] = useState(user.firstName)
  const [email, setEmail] = useState(user.email)
  const [phoneNumber, setPhoneNumber] = useState(user.phoneNumber)

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

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
        })
        .finally(() => {
          setIsModalOpened(false)
        })
    },
    [
      firstName,
      lastName,
      email,
      phoneNumber,
      setUserInformations,
      user,
      showSuccessNotification,
      setIsModalOpened,
    ]
  )

  const handleLastNameChange = useCallback(
    event => {
      setLastName(event.target.value)
    },
    [setLastName]
  )

  const handleFirstNameChange = useCallback(
    event => {
      setFirstName(event.target.value)
    },
    [setFirstName]
  )

  const handleEmailChange = useCallback(
    event => {
      setEmail(event.target.value)
    },
    [setEmail]
  )

  const handlePhoneNumberChange = useCallback(
    event => {
      setPhoneNumber(event.target.value)
    },
    [setPhoneNumber]
  )

  return (
    <DialogBox
      labelledBy="modal profile"
      onDismiss={closeModal}
    >
      <div className="profile-info-modal">
        <div className="pi-title">
          {'Profil'}
        </div>
        <div className="pi-mandatory-message">
          {'Tous les champs sont obligatoires'}
        </div>
        <form onSubmit={submitProfileInformations}>
          <TextInput
            label="Nom"
            name="last-name-input"
            onChange={handleLastNameChange}
            value={lastName}
          />
          <TextInput
            label="Prénom"
            name="first-name-input"
            onChange={handleFirstNameChange}
            value={firstName}
          />
          <TextInput
            label="Email"
            name="email-input"
            onChange={handleEmailChange}
            value={email}
          />
          <TextInput
            label="Téléphone"
            name="phone-input"
            onChange={handlePhoneNumberChange}
            value={phoneNumber}
          />
          <div className="actions-group">
            <button
              className="secondary-button"
              onClick={closeModal}
              type="button"
            >
              {'Annuler'}
            </button>
            <button
              className="primary-button"
              type="submit"
            >
              {'Enregistrer'}
            </button>
          </div>
        </form>
      </div>
    </DialogBox>
  )
}

ProfileInformationsModal.propTypes = {
  setIsModalOpened: PropTypes.func.isRequired,
  setUserInformations: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
  user: PropTypes.shape().isRequired,
}

export default ProfileInformationsModal
