import { Outlet } from 'react-router'

import { FullPageLayout } from '@/app/App/layouts/funnels/FullPageLayout/FullPageLayout'

export const WelcomeCarousel = (): JSX.Element => {
  return (
    <FullPageLayout>
      <Outlet />
    </FullPageLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeCarousel
