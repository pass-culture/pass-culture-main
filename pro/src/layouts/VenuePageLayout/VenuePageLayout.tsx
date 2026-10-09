import { Outlet, useLocation } from 'react-router'

import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'

import { Header } from '../CollectiveVenuePageLayout/components/Header'
import styles from './VenuePageLayout.module.scss'

export const VenuePageLayout = () => {
  const location = useLocation()

  const context = location.pathname.includes('page-collective')
    ? 'collective'
    : 'partnerPage'
  const titleText =
    context === 'collective' ? 'Page dans ADAGE' : 'Page sur l’application'

  return (
    <ContentLayout>
      <h1 className={styles['title']}>{titleText}</h1>
      <div>
        <Header context={context} />

        <Outlet />
      </div>
    </ContentLayout>
  )
}
