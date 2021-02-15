import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { DialogBox } from '../../layout/DialogBox/DialogBox'
import TextInput from '../../layout/inputs/TextInput/TextInput'

const ProfileInformationsModal = ({ setIsModalOpened }) => {
  const [lastName, setLastName] = useState('')
  const [firstName, setFirstName] = useState('')
  const [email, setEmail] = useState('')
  const [phoneNumber, setPhoneNumber] = useState('')

  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  const submitProfileInformations = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  const handleLastNameChange = useCallback(event => {
    setLastName(event.target.value)
  }, [])

  const handleFirstNameChange = useCallback(event => {
    setFirstName(event.target.value)
  }, [])

  const handleEmailChange = useCallback(event => {
    setEmail(event.target.value)
  }, [])

  const handlePhoneNumberChange = useCallback(event => {
    setPhoneNumber(event.target.value)
  }, [])

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
              onClick={submitProfileInformations}
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
}

export default ProfileInformationsModal
