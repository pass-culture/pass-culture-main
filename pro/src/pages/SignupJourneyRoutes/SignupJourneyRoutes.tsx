import { useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router'

import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import {
  SignupJourneyContextProvider,
  useSignupJourneyContext,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
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
  const isSignupSimulationEnabled = useActiveFeature(
    'WIP_PRE_SIGNUP_SIMULATION'
  )

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
        {isSignupSimulationEnabled ? (
          <Outlet />
        ) : (
          // TODO: (jclery, 2026-04-29): Remove all of this with WIP_PRE_SIGNUP_SIMULATION once the feature is enabled
          <div className={styles['content-with-stepper']}>
            {location.pathname.includes(
              '/inscription/structure/rattachement'
            ) ? null : (
              <MainHeading mainHeading="Votre structure" />
            )}
            <SignupJourneyStepper />
            <Outlet />
          </div>
        )}
      </SignupJourneyContextProvider>
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = SignupJourneyRoutes
