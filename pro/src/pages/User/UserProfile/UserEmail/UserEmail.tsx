import { useEffect, useState } from 'react'

import { api } from '@/apiClient/api'
import { SummarySection } from '@/components/SummaryLayout/SummarySection'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import { UserEmailForm } from '@/pages/User/UserProfile/UserEmail/UserEmailForm/UserEmailForm'

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
  const [pendingEmailValidation, setPendingEmailValidation] =
    useState<string>('')

  const getPendingEmailRequest = async () => {
    const response = await api.getUserEmailPendingValidation()
    const newEmail = response.newEmail || ''
    setPendingEmailValidation(newEmail)
  }

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getPendingEmailRequest()
  }, [])

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
      {showForm ? (
        <UserEmailForm
          closeForm={resetForm}
          getPendingEmailRequest={getPendingEmailRequest}
        />
      ) : (
        initialValues.email
      )}
      {!showForm && pendingEmailValidation && (
        <BannerPendingEmailValidation email={pendingEmailValidation} />
      )}
    </SummarySection>
  )
}
