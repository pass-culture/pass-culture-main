import { Outlet, useLocation } from 'react-router'

import { FullPageLayout } from '@/app/App/layouts/funnels/FullPageLayout/FullPageLayout'
import { SimulatorContextProvider } from '@/pages/Simulator/SimulatorContext'

import styles from './Simulator.module.scss'
import { SimulatorContextProvider } from './SimulatorContext'

export const Simulator = (): JSX.Element => {
  const location = useLocation()
  const stepTitles: Record<string, string> = {
    '/inscription/preparation/siret':
      'Préparation de l’inscription - Étape 1 sur 3',
    '/inscription/preparation/activite':
      'Préparation de l’inscription - Étape 2 sur 3',
    '/inscription/preparation/publics':
      'Préparation de l’inscription - Étape 3 sur 3',
  }
  return (
    <FullPageLayout>
      <div className={styles['simulator-container']}>
        <div className={styles['step-title']}>
          {stepTitles[location.pathname]}
        </div>
        <SimulatorContextProvider>
          <Outlet />
        </SimulatorContextProvider>
      </div>
    </FullPageLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Simulator
