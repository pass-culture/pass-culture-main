import { BoxFormLayout } from 'components/BoxFormLayout/BoxFormLayout'
import { UserPasswordForm } from 'components/UserPasswordForm/UserPasswordForm'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'

import { Forms } from './constants'

interface UserPasswordProps {
  setCurrentForm: (value: Forms | null) => void
  showForm: boolean
}

export const UserPassword = ({
  setCurrentForm,
  showForm = false,
}: UserPasswordProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_PASSWORD)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
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
