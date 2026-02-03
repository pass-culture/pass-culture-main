import type { UserIdentityFormValues } from '@/components/UserIdentityForm/types'
import { UserIdentityForm } from '@/components/UserIdentityForm/UserIdentityForm'
import { BoxFormLayout } from '@/ui-kit/BoxFormLayout/BoxFormLayout'

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
      {showForm ? (
        <UserIdentityForm closeForm={resetForm} initialValues={initialValues} />
      ) : (
        <BoxFormLayout.Header
          subtitle={`${initialValues.firstName} ${initialValues.lastName}`}
          title="Prénom et nom"
          onClickModify={onClickModify}
        />
      )}
    </BoxFormLayout>
  )
}
