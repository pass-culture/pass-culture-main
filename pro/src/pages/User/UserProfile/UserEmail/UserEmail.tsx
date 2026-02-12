import useSWR from 'swr'

import { api } from '@/apiClient/api'
import { GET_USER_EMAIL_PENDING_VALIDATION } from '@/commons/config/swrQueryKeys'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { UserEmailForm } from '@/pages/User/UserProfile/UserEmail/UserEmailForm/UserEmailForm'
import { SummarySection } from '@/ui-kit/SummaryLayout/SummarySection'

import { Forms } from '../constants'
import { BannerPendingEmailValidation } from './BannerPendingEmailValidation/BannerPendingEmailValidation'

export interface UserEmailInitialValues {
  email: string
}

interface UserEmailProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserEmailInitialValues
  showForm: boolean
}

export const UserEmail = ({
  setCurrentForm,
  initialValues,
  showForm = false,
}: UserEmailProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_EMAIL)
  const resetForm = () => setCurrentForm(null)

  const { data: pendingEmailValidation } = useSWR(
    [GET_USER_EMAIL_PENDING_VALIDATION],
    () => api.getUserEmailPendingValidation()
  )

  return (
    <SummarySection
      title={'Adresse email de connexion'}
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
      {showForm ? <UserEmailForm closeForm={resetForm} /> : initialValues.email}
      {!showForm && pendingEmailValidation?.newEmail && (
        <BannerPendingEmailValidation email={pendingEmailValidation.newEmail} />
      )}
    </SummarySection>
  )
}
