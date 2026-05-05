import { useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router'

import { FullPageLayout } from '@/app/App/layouts/funnels/FullPageLayout/FullPageLayout'
import { FunnelLayout } from '@/app/App/layouts/funnels/FunnelLayout/FunnelLayout'
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

  if (isSignupSimulationEnabled) {
    return (
      <FullPageLayout>
        <SignupJourneyContextProvider>
          <Outlet />
        </SignupJourneyContextProvider>
      </FullPageLayout>
    )
  }

  // TODO: (jclery, 2026-04-29): Remove this with WIP_PRE_SIGNUP_SIMULATION once the feature is enabled
  return (
    <FunnelLayout
      mainHeading={
        location.pathname.includes('/inscription/structure/rattachement')
          ? null
          : 'Votre structure'
      }
      hideAdminButton
    >
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
