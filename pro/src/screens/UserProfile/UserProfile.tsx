import { IUserIdentityFormValues } from 'new_components/ProfileForm/types'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'
import { ProfileForm } from 'new_components/ProfileForm'
import React from 'react'

interface IUserProfileProps {
  patchIdentityAdapter: PatchIdentityAdapter
  userIdentityInitialValues: IUserIdentityFormValues
}

const UserProfile = ({
  patchIdentityAdapter,
  userIdentityInitialValues,
}: IUserProfileProps): JSX.Element => {
  return (
    <>
      <h1>Profil</h1>
      <ProfileForm
        title="Prénom et nom"
        subtitleFormat={values => `${values.firstName} ${values.lastName}`}
        initialValues={userIdentityInitialValues}
        patchIdentityAdapter={patchIdentityAdapter}
      />
    </>
  )
}

export default UserProfile
