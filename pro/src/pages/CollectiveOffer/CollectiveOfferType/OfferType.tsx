import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'

import { OfferTypeScreen } from './OfferType/OfferType'
import styles from './OfferType.module.scss'

export const OfferType = (): JSX.Element => (
  <ContentLayout>
    <h1 className={styles['title']}>Créer une offre collective</h1>
    <OfferTypeScreen />
  </ContentLayout>
)

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
