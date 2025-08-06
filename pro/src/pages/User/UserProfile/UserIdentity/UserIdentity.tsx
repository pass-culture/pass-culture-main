import { UserIdentityFormValues } from '@/components/UserIdentityForm/types'
import { UserIdentityForm } from '@/components/UserIdentityForm/UserIdentityForm'
import { BoxFormLayout } from '@/ui-kit/BoxFormLayout/BoxFormLayout'
import { BoxRounded } from '@/ui-kit/BoxRounded/BoxRounded'

import { Forms } from '../constants'

interface UserIdentityProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserIdentityFormValues
  showForm: boolean
}

export const UserIdentity = ({
  setCurrentForm,
  initialValues,
  showForm,
}: UserIdentityProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_IDENTITY)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={!showForm ? onClickModify : undefined}>
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
