import { useEffect, useState } from 'react'

import { BannerPendingEmailValidation } from 'new_components/Banner'
import { BoxFormLayout } from 'new_components/BoxFormLayout'
import { UserEmailForm } from 'new_components/UserEmailForm'
import { getPendingEmailValidationAdapter } from 'routes/User/adapters/getPendingEmailValidationAdapter'
import postEmailAdapter from 'routes/User/adapters/postEmailAdapter'
import { BoxRounded } from 'ui-kit/BoxRounded'

import { Forms } from '../constants'

export interface IUserEmailInitialValues {
  email: string
}

interface IUserEmailProps {
  setCurrentForm: (value: Forms | null) => void
  initialValues: IUserEmailInitialValues
  showForm: boolean
}

const UserEmail = ({
  setCurrentForm,
  initialValues,
  showForm = false,
}: IUserEmailProps) => {
  const onClickModify = () => setCurrentForm(Forms.USER_EMAIL)
  const resetForm = () => setCurrentForm(null)
  const [pendingEmailValidation, setPendingEmailValidation] =
    useState<string>('')
  const getPendingEmailRequest = () => {
    getPendingEmailValidationAdapter().then(response => {
      const newEmail = response.payload?.newEmail || ''
      setPendingEmailValidation(newEmail)
    })
  }
  useEffect(() => {
    getPendingEmailRequest()
  }, [])

  return (
    <BoxFormLayout>
      <BoxRounded onClickModify={onClickModify} showButtonModify={!showForm}>
        {showForm ? (
          <UserEmailForm
            closeForm={resetForm}
            postEmailAdapter={postEmailAdapter}
            getPendingEmailRequest={getPendingEmailRequest}
          />
        ) : (
          <>
            <BoxFormLayout.Header
              subtitle={initialValues.email}
              title="Adresse e-mail"
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
