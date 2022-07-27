import { ProfileForm } from 'new_components/ProfileForm'
import React from 'react'
import { UserIdentityResponseModel } from 'apiClient/v1'
import patchIdentityAdapter from 'routes/User/adapters/patchIdentityAdapter'

const UserProfile = ({
  ...identityData
}: UserIdentityResponseModel): JSX.Element => {
  return (
    <>
      <h1>Profil</h1>
      <ProfileForm
        title="Prénom et nom"
        subtitleFormat={values => `${values.firstName} ${values.lastName}`}
        initialValues={{
          firstName: identityData.firstName,
          lastName: identityData.lastName,
        }}
        adapter={patchIdentityAdapter}
      />
    </>
  )
}

export default UserProfile
