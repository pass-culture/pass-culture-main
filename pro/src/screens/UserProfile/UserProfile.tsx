import React from 'react'

import { UserIdentityForm } from 'new_components/UserIdentityForm'
import { IUserIdentityFormValues } from 'new_components/UserIdentityForm/types'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'

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
      <UserIdentityForm
        title="Prénom et nom"
        subtitleFormat={values => `${values.firstName} ${values.lastName}`}
        initialValues={userIdentityInitialValues}
        patchIdentityAdapter={patchIdentityAdapter}
      />
    </>
  )
}

export default UserProfile
