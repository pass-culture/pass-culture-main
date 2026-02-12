import type { UserIdentityFormValues } from '@/components/UserIdentityForm/types'
import { UserIdentityForm } from '@/components/UserIdentityForm/UserIdentityForm'
import { Panel } from '@/ui-kit/Panel/Panel'

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
    <Panel>
      {showForm ? (
        <UserIdentityForm closeForm={resetForm} initialValues={initialValues} />
      ) : (
        <Panel.Header
          subtitle={`${initialValues.firstName} ${initialValues.lastName}`}
          title="Prénom et nom"
          onClickModify={onClickModify}
        />
      )}
    </Panel>
  )
}
