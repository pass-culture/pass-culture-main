import type { UserIdentityFormValues } from '@/components/UserIdentityForm/types'
import { UserIdentityForm } from '@/components/UserIdentityForm/UserIdentityForm'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'

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
    <SummarySection
      title={'Prénom et nom'}
      editLink={
        <Button
          label="Modifier"
          onClick={onClickModify}
          variant={ButtonVariant.SECONDARY}
          color={ButtonColor.NEUTRAL}
          size={ButtonSize.SMALL}
        />
      }
      shouldShowDivider={true}
    >
      {showForm ? (
        <UserIdentityForm closeForm={resetForm} initialValues={initialValues} />
      ) : (
        <p>{`${initialValues.firstName} ${initialValues.lastName}`}</p>
      )}
    </SummarySection>
  )
}
