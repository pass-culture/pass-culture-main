// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import React, { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { AppLayout } from 'app/AppLayout'
import { EmailChangeValidationScreen } from 'screens/EmailChangeValidation/EmailChangeValidation'
import { updateUser } from 'store/user/reducer'
import { parse } from 'utils/query-string'

const EmailChangeValidation = (): JSX.Element => {
  const [isSuccess, setIsSuccess] = useState<boolean | undefined>(undefined)
  const location = useLocation()
  const dispatch = useDispatch()

  useEffect(() => {
    const changeEmail = async () => {
      const { expiration_timestamp, token } = parse(location.search)
      const expiration_date = new Date(expiration_timestamp || '')
      const now = new Date(Date.now() / 1000)
      if (expiration_date > now) {
        setIsSuccess(false)
        return
      }

      try {
        await api.patchValidateEmail({ token: token || '' })
        setIsSuccess(true)
        dispatch(updateUser(null))
      } catch {
        setIsSuccess(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    changeEmail()
  }, [])

  if (isSuccess === undefined) {
    return <></>
  }

  return (
    <AppLayout layout="without-nav">
      <EmailChangeValidationScreen isSuccess={isSuccess} />
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = EmailChangeValidation
