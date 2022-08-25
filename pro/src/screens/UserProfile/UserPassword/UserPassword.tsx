import { BoxFormLayout } from 'new_components/BoxFormLayout'
import { UserPasswordForm } from 'new_components/UserPasswordForm'
import postPasswordAdapter from 'routes/User/adapters/postPasswordAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from '../constants'

interface IUserPasswordProps {
  setCurrentForm: (value: Forms | null) => void
  showForm: boolean
}

const UserPassword = ({
  setCurrentForm,
  showForm = false,
}: IUserPasswordProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_PASSWORD)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserPasswordForm
            closeForm={resetForm}
            postPasswordAdapter={postPasswordAdapter}
          />
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

export default UserPassword
