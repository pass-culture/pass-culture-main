import { UserPasswordForm } from '@/components/UserPasswordForm/UserPasswordForm'
import { BoxFormLayout } from '@/ui-kit/BoxFormLayout/BoxFormLayout'
import { BoxRounded } from '@/ui-kit/BoxRounded/BoxRounded'

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
      <BoxRounded onClickModify={!showForm ? onClickModify : undefined}>
        {showForm ? (
          <UserPasswordForm closeForm={resetForm} />
        ) : (
          <BoxFormLayout.Header
            subtitle="***************"
            title="Mot de passe"
          />
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}
