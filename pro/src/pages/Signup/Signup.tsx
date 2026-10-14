import { Outlet } from 'react-router'

import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'

export const Signup = () => {
  return (
    <FullLayout>
      <Outlet />
    </FullLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Signup
