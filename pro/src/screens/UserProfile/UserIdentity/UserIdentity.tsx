import { BoxFormLayout } from 'components/BoxFormLayout/BoxFormLayout'
import { UserIdentityForm } from 'components/UserIdentityForm'
import { UserIdentityFormValues } from 'components/UserIdentityForm/types'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'

import { Forms } from '../constants'

interface UserIdentityProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserIdentityFormValues
  showForm: boolean
}

const UserIdentity = ({
  setCurrentForm,
  initialValues,
  showForm = false,
}: UserIdentityProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_IDENTITY)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserIdentityForm
            closeForm={resetForm}
            initialValues={initialValues}
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
