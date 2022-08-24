// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import React, { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useLocation } from 'react-router'

import { api } from 'apiClient/api'
import { EmailChangeValidationScreen } from 'screens/EmailChangeValidation'
import { resetIsInitialized } from 'store/user/actions'
import { parse } from 'utils/query-string'

const EmailChangeValidation = (): JSX.Element => {
  const [isSuccess, setIsSuccess] = useState<boolean | undefined>(undefined)
  const location = useLocation()
  const dispatch = useDispatch()
  useEffect(() => {
    const { expiration_timestamp, token } = parse(location.search)
    const expiration_date = new Date(expiration_timestamp)
    const now = new Date(Date.now() / 1000)
    if (expiration_date > now) {
      setIsSuccess(false)
      return
    }
    api
      .patchValidateEmail({ token: token })
      .then(() => {
        setIsSuccess(true)
        dispatch(resetIsInitialized())
      })
      .catch(() => setIsSuccess(false))
  }, [])

  if (isSuccess === undefined) return <></>
  return <EmailChangeValidationScreen isSuccess={isSuccess} />
}

export default EmailChangeValidation
