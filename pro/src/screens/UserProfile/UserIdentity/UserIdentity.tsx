import { BoxFormLayout } from 'new_components/BoxFormLayout'
import { UserIdentityForm } from 'new_components/UserIdentityForm'
import { IUserIdentityFormValues } from 'new_components/UserIdentityForm/types'
import patchIdentityAdapter from 'routes/User/adapters/patchIdentityAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from '../constants'

interface IUserIdentityProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: IUserIdentityFormValues
  showForm: boolean
}

const UserIdentity = ({
  setCurrentForm,
  initialValues,
  showForm = false,
}: IUserIdentityProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_IDENTITY)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserIdentityForm
            closeForm={resetForm}
            initialValues={initialValues}
            patchIdentityAdapter={patchIdentityAdapter}
          />
        ) : (
          <BoxFormLayout.Header
            subtitle={`${initialValues.firstName} ${initialValues.lastName}`}
            title="Prénom et nom"
          />
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}

export default UserIdentity
