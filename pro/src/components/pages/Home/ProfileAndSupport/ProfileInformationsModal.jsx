import PropTypes from 'prop-types'
import React from 'react'

import DialogBox from 'new_components/DialogBox/DialogBox'

import ProfileForm from './ProfileForm'

const ProfileInformationsModal = ({ hideProfileInfoModal, user }) => {
  const initialValues = {
    lastName: user.lastName || '',
    firstName: user.firstName || '',
    email: user.email || '',
    phoneNumber: user.phoneNumber || '',
  }

  return (
    <DialogBox labelledBy="modal-profile" onDismiss={hideProfileInfoModal}>
      <div className="profile-info-modal">
        <h1 className="pi-title" id="modal-profile">
          Profil
        </h1>
        <ProfileForm
          initialValues={initialValues}
          onCancel={hideProfileInfoModal}
          onSuccess={hideProfileInfoModal}
        />
      </div>
    </DialogBox>
  )
}

ProfileInformationsModal.propTypes = {
  hideProfileInfoModal: PropTypes.func.isRequired,
  user: PropTypes.shape({
    firstName: PropTypes.string,
    lastName: PropTypes.string,
    email: PropTypes.string,
    phoneNumber: PropTypes.string,
  }).isRequired,
}

export default ProfileInformationsModal
