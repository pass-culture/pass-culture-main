import { UserPasswordForm } from '@/components/UserPasswordForm/UserPasswordForm'
import { BoxFormLayout } from '@/ui-kit/BoxFormLayout/BoxFormLayout'

import { Forms } from '../constants'

interface UserPasswordProps {
  setCurrentForm: (value: Forms | null) => void
  showForm: boolean
}

export const UserPassword = ({
  setCurrentForm,
  showForm,
}: UserPasswordProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_PASSWORD)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      {showForm ? (
        <UserPasswordForm closeForm={resetForm} />
      ) : (
        <BoxFormLayout.Header
          onClickModify={onClickModify}
          subtitle="***************"
          title="Mot de passe"
        />
      )}
    </BoxFormLayout>
  )
}
