/* istanbul ignore file */

import { Outlet, useLocation } from 'react-router'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Stepper } from '@/design-system/Stepper/Stepper'

import styles from './IndividualOfferV2.module.scss'

export const IndividualOfferV2 = () => {
  const { pathname } = useLocation()

  return (
    <IndividualOfferContextProvider>
      <FullLayout>
        <div className={styles['content-wrapper']}>
          <h1 className={styles['title']}>Créer une offre</h1>
          <div className={styles['stepper-wrapper']}>
            <Stepper
              activeStep={pathname.split('/').pop() ?? ''}
              steps={[
                {
                  id: 'nature-format-domaine',
                  label: 'Nature et format',
                  url: '/offre/individuelle/v2/creation/nature-format-domaine',
                },
                {
                  id: 'description',
                  label: 'Description',
                  url: '/offre/individuelle/v2/creation/description',
                },
                {
                  id: 'tarifs-modalites',
                  label: 'Tarif et modalités',
                  url: '/offre/individuelle/v2/:offerId/creation/tarifs-modalites',
                },
                {
                  id: 'recapitulatif',
                  label: 'Récapitulatif',
                },
                { id: 'publication', label: 'Publication' },
              ]}
            />
          </div>
          <div className={styles['content']}>
            <Outlet />
          </div>
        </div>
      </FullLayout>
    </IndividualOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferV2
