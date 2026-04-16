import { RouterProvider } from 'react-router'

import { router } from '@/index'

export const AppRouter = (): JSX.Element => {
  return <RouterProvider router={router} />
}
