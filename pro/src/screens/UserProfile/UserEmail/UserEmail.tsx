import { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { BannerPendingEmailValidation } from 'components/Banner'
import { BoxFormLayout } from 'components/BoxFormLayout'
import { UserEmailForm } from 'components/UserEmailForm'
import { BoxRounded } from 'ui-kit/BoxRounded/BoxRounded'

import { Forms } from '../constants'

export interface UserEmailInitialValues {
  email: string
}

interface UserEmailProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: UserEmailInitialValues
  showForm: boolean
}

const UserEmail = ({
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
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserEmailForm
            closeForm={resetForm}
            getPendingEmailRequest={getPendingEmailRequest}
          />
        ) : (
          <>
            <BoxFormLayout.Header
              subtitle={initialValues.email}
              title="Adresse email de connexion"
            />
            {pendingEmailValidation && (
              <BoxFormLayout.Banner
                banner={
                  <BannerPendingEmailValidation
                    email={pendingEmailValidation}
                  />
                }
              />
            )}
          </>
        )}
      </BoxRounded>
    </BoxFormLayout>
  )
}

export default UserEmail
