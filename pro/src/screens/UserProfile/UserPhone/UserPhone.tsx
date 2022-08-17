import { UserPhoneBodyModel } from 'apiClient/v1'
import { formatPhoneNumber } from 'components/pages/Home/ProfileAndSupport/ProfileAndSupport'
import { BoxFormLayout } from 'new_components/BoxFormLayout'
import { UserPhoneForm } from 'new_components/UserPhoneForm'
import patchPhoneAdapter from 'routes/User/adapters/patchPhoneAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from '../constants'

interface IUserPhoneProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserPhoneBodyModel
  showForm: boolean
}

const UserPhone = ({
  setCurrentForm,
  initialValues,
  showForm = false,
}: IUserPhoneProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_PHONE)
  const resetForm = () => setCurrentForm(null)
  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserPhoneForm
            closeForm={resetForm}
            initialValues={initialValues}
            patchPhoneAdapter={patchPhoneAdapter}
          />
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

export default UserPhone
