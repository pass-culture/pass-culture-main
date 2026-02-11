import { UserPasswordForm } from '@/components/UserPasswordForm/UserPasswordForm'
import { Panel } from '@/ui-kit/Panel/Panel'

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
    <Panel>
      {showForm ? (
        <UserPasswordForm closeForm={resetForm} />
      ) : (
        <Panel.Header
          onClickModify={onClickModify}
          subtitle="***************"
          title="Mot de passe"
        />
      )}
    </Panel>
  )
}
