import { Outlet } from 'react-router'

import { SignupFunnelLayout } from '@/app/App/layouts/funnels/SignupFunnelLayout/SignupFunnelLayout'

export const WelcomeCarousel = (): JSX.Element => {
  return (
    <SignupFunnelLayout>
      <Outlet />
    </SignupFunnelLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeCarousel
