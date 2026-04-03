import { useEffect } from 'react'
import { Outlet, useBlocker, useLocation, useNavigate } from 'react-router'

import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import {
  cleanSignupJourneyStorage,
  SignupJourneyContextProvider,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { SignupJourneyStepper } from '@/components/SignupJourneyStepper/SignupJourneyStepper'

import styles from './SignupJourneyRoutes.module.scss'

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
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        navigate('/inscription/structure/recherche')
      }
    }
  }, [offerer?.siren, offerer?.siret, location.pathname, navigate, setOfferer])

  // If the user leaves the signup journey, clear the saved data
  const blocker = useBlocker(
    ({ nextLocation }) =>
      nextLocation.pathname.startsWith('/inscription/structure') === false
  )
  useEffect(() => {
    if (blocker.state === 'blocked') {
      console.log('Leaving signup journey, clearing storage …')
      // Clear saved data for signup journey
      cleanSignupJourneyStorage()
      blocker.proceed()
    }
  }, [blocker])

  return (
    <FunnelLayout mainHeading="Votre structure" hideAdminButton>
      <SignupJourneyContextProvider>
        <div className={styles['content-with-stepper']}>
          <SignupJourneyStepper />
          <Outlet />
        </div>
      </SignupJourneyContextProvider>
    </FunnelLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SignupJourneyRoutes
