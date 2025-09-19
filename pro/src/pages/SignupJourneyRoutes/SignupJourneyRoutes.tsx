import { useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router'

import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
import {
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

  return (
    <FunnelLayout mainHeading="Votre structure">
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
