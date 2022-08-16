import { UserIdentityForm } from 'new_components/UserIdentityForm'
import { IUserIdentityFormValues } from 'new_components/UserIdentityForm/types'
import { PatchIdentityAdapter } from 'routes/User/adapters/patchIdentityAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from '../constants'

import { UserIdentityDetails } from './UserIdentityDetails'

interface IUserIdentityProps {
  onClickModify: () => void
  initialValues: IUserIdentityFormValues
  patchIdentityAdapter: PatchIdentityAdapter // may directly be import on this directory (and may be defined).
  showForm: boolean
}

const UserIdentity = ({
  onClickModify,
  initialValues,
  patchIdentityAdapter,
  showForm = false,
}: IUserIdentityProps) => {
  return (
    <BoxRounded onClickModify={onClickModify}>
      {showForm ? (
        <UserIdentityForm
          title="Prénom et nom"
          subtitleFormat={values => `${values.firstName} ${values.lastName}`}
          initialValues={initialValues}
          patchIdentityAdapter={patchIdentityAdapter}
        />
      ) : (
        <UserIdentityDetails />
      )}
    </BoxRounded>
  )
}

export default UserIdentity
