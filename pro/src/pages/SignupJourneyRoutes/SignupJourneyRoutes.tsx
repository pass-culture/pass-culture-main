import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Outlet } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'
import { SignupJourneyContextProvider } from 'commons/context/SignupJourneyContext/SignupJourneyContext'
import { selectCurrentUser } from 'commons/store/user/selectors'
import { Header } from 'components/Header/Header'
import { SignupJourneyFormLayout } from 'components/SignupJourneyFormLayout/SignupJourneyFormLayout'

export const SignupJourneyRoutes = () => {
  const currentUser = useSelector(selectCurrentUser)

  useEffect(() => {
    if (window.Beamer !== undefined) {
      window.Beamer.hide()
    }

    return () => {
      if (window.Beamer !== undefined) {
        window.Beamer.show()
      }
    }
  }, [])
  return (
    <>
      <Layout layout="funnel">
        <Header disableHomeLink={!currentUser?.hasUserOfferer} />
        <SignupJourneyContextProvider>
          <SignupJourneyFormLayout>
            <Outlet />
          </SignupJourneyFormLayout>
        </SignupJourneyContextProvider>
      </Layout>
    </>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = SignupJourneyRoutes
