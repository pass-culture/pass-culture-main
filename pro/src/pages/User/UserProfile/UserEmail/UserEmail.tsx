import { api } from 'apiClient/api'
import { UserEmailForm } from 'pages/User/UserProfile/UserEmail/UserEmailForm/UserEmailForm'
import { useEffect, useState } from 'react'
import { BoxFormLayout } from 'ui-kit/BoxFormLayout/BoxFormLayout'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'

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
    <BoxFormLayout>
      <BoxRounded
        onClickModify={!showForm ? onClickModify : undefined}
        footer={
          !showForm &&
          pendingEmailValidation && (
            <BannerPendingEmailValidation email={pendingEmailValidation} />
          )
        }
      >
        {showForm ? (
          <UserEmailForm
            closeForm={resetForm}
            getPendingEmailRequest={getPendingEmailRequest}
          />
        ) : (
          <BoxFormLayout.Header
            subtitle={initialValues.email}
            title="Adresse email de connexion"
          />
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}
