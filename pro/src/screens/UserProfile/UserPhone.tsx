import { UserPhoneBodyModel } from 'apiClient/v1'
import { BoxFormLayout } from 'components/BoxFormLayout/BoxFormLayout'
import { UserPhoneForm } from 'components/UserPhoneForm/UserPhoneForm'
import { formatPhoneNumber } from 'pages/Home/ProfileAndSupport/Profile'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'

import { Forms } from './constants'

interface UserPhoneProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserPhoneBodyModel
  showForm: boolean
}

export const UserPhone = ({
  setCurrentForm,
  initialValues,
  showForm = false,
}: UserPhoneProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_PHONE)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserPhoneForm closeForm={resetForm} initialValues={initialValues} />
        ) : (
          <BoxFormLayout.Header
            subtitle={`${formatPhoneNumber(initialValues.phoneNumber)}`}
            title="Téléphone"
          />
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}
