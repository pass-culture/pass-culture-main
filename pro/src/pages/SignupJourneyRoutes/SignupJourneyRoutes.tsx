import { useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import {
  SignupJourneyContextProvider,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'

export const SignupJourneyRoutes = () => {
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

  const location = useLocation()
  const navigate = useNavigate()
  const { offerer, setOfferer } = useSignupJourneyContext()

  useEffect(() => {
    if (!location.pathname.includes('/inscription/structure/recherche')) {
      if (offerer?.siret === '' || offerer?.siren === '') {
        setOfferer(null)
        navigate('/inscription/structure/recherche')
      }
    }
  }, [offerer?.siren, offerer?.siret, location.pathname, navigate, setOfferer])

  return (
    <FullLayout>
      <SignupJourneyContextProvider>
        <Outlet />
      </SignupJourneyContextProvider>
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SignupJourneyRoutes
