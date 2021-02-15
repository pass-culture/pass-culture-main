import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import { DialogBox } from '../../layout/DialogBox/DialogBox'
import TextInput from '../../layout/inputs/TextInput/TextInput'

const ProfileInformationsModal = ({ setIsModalOpened }) => {
  const closeModal = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

  const submitProfileInformations = useCallback(() => {
    setIsModalOpened(false)
  }, [setIsModalOpened])

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
          />
          <TextInput
            label="Prénom"
            name="first-name-input"
          />
          <TextInput
            label="Email"
            name="email-input"
          />
          <TextInput
            label="Téléphone"
            name="phone-input"
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
