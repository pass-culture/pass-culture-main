import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { UserPasswordForm } from '@/components/UserPasswordForm/UserPasswordForm'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'

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
    <SummarySection
      title={'Mot de passe'}
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
        <UserPasswordForm closeForm={resetForm} />
      ) : (
        <>
          <p>Mot de passe</p>
          <p>***************</p>
        </>
      )}
    </SummarySection>
  )
}
