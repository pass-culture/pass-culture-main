import { BoxFormLayout } from 'components/BoxFormLayout'
import { UserPasswordForm } from 'components/UserPasswordForm'
import postPasswordAdapter from 'pages/User/adapters/postPasswordAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from '../constants'

interface UserPasswordProps {
  setCurrentForm: (value: Forms | null) => void
  showForm: boolean
}

const UserPassword = ({
  setCurrentForm,
  showForm = false,
}: UserPasswordProps) => {
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
