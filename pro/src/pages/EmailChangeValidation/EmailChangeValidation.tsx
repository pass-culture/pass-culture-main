// react hooks and usages doc : https://reactjs.org/docs/hooks-intro.html
import { useEffect, useState } from 'react'
import { useDispatch } from 'react-redux'
import { useLocation } from 'react-router'

import { api } from 'apiClient/api'
import { Layout } from 'app/App/layout/Layout'
import { updateUser } from 'commons/store/user/reducer'
import { parse } from 'commons/utils/query-string'

import { EmailChangeValidationScreen } from './components/EmailChangeValidation/EmailChangeValidation'

const EmailChangeValidation = (): JSX.Element => {
  const [isSuccess, setIsSuccess] = useState<boolean | undefined>(undefined)
  const location = useLocation()
  const dispatch = useDispatch()

  useEffect(() => {
    const changeEmail = async () => {
      const { expiration_timestamp, token } = parse(location.search)
      const expiration_date = new Date(expiration_timestamp)
      const now = new Date(Date.now() / 1000)
      if (expiration_date > now) {
        setIsSuccess(false)
        return
      }

      try {
        await api.patchValidateEmail({ token: token })
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
    <Layout
      layout="logged-out"
      mainHeading={isSuccess ? 'Et voilà !' : 'Votre lien a expiré !'}
    >
      <EmailChangeValidationScreen isSuccess={isSuccess} />
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = EmailChangeValidation
