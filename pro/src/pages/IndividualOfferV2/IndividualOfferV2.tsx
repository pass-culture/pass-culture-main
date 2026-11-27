/* istanbul ignore file */

import { useEffect } from 'react'
import { Outlet, useLocation, useParams } from 'react-router'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { resetNFD } from '@/commons/store/nfd/reducer'
import { Stepper } from '@/design-system/Stepper/Stepper'

import styles from './IndividualOfferV2.module.scss'

export const IndividualOfferV2 = () => {
  const { pathname } = useLocation()
  const { offerId } = useParams<{ offerId: string }>()
  const dispatch = useAppDispatch()
  const offerPathPrefix = offerId
    ? `/offre/individuelle/v2/${offerId}`
    : '/offre/individuelle/v2'

  useEffect(() => {
    return () => {
      dispatch(resetNFD())
    }
  }, [dispatch])

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
                  url: `${offerPathPrefix}/creation/nature-format-domaine`,
                },
                {
                  id: 'description',
                  label: 'Description',
                  url: `${offerPathPrefix}/creation/description`,
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
