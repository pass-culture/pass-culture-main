import React, { useState } from 'react'
import { FormSpy } from 'react-final-form'

import { UserIdentityForm } from 'new_components/UserIdentityForm'
import { IUserIdentityFormValues } from 'new_components/UserIdentityForm/types'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from './constants'
import { UserIdentity } from './UserIdentity'

interface IUserProfileProps {
  patchIdentityAdapter: PatchIdentityAdapter
  userIdentityInitialValues: IUserIdentityFormValues
}

// test
const UserProfile = ({
  patchIdentityAdapter,
  userIdentityInitialValues,
}: IUserProfileProps): JSX.Element => {
  const [currentForm, setCurrentFrom] = useState<Forms | null>(null)

  return (
    <>
      <h1>Profil</h1>

      <UserIdentity
        onClickModify={() => setCurrentFrom(Forms.USER_IDENTITY)}
        initialValues={userIdentityInitialValues}
        patchIdentityAdapter={patchIdentityAdapter}
      />
    </>
  )
}

export default UserProfile
