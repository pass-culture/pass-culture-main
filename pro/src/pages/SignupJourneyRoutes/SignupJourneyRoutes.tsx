import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Outlet } from 'react-router'

import { Header } from '@/app/App/layouts/components/Header/Header'
import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import { SignupJourneyContextProvider } from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { selectCurrentUser } from '@/commons/store/user/selectors'
import { SignupJourneyFormLayout } from '@/components/SignupJourneyFormLayout/SignupJourneyFormLayout'

export const SignupJourneyRoutes = () => {
  const currentUser = useSelector(selectCurrentUser)

  useEffect(() => {
    if (window.Beamer?.config) {
      window.Beamer.hide()
    }

    return () => {
      if (window.Beamer?.config) {
        window.Beamer.show()
      }
    }
  }, [])
  return (
    <FunnelLayout>
      <Header disableHomeLink={!currentUser?.hasUserOfferer} />
      <SignupJourneyContextProvider>
        <SignupJourneyFormLayout>
          <Outlet />
        </SignupJourneyFormLayout>
      </SignupJourneyContextProvider>
    </FunnelLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SignupJourneyRoutes
