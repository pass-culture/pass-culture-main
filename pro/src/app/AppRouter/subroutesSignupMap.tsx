import {
  generatePath,
  Navigate,
  type NavigateProps,
  useParams,
} from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { noop } from '@/commons/utils/noop'

import { validateSignupActivation } from './middlewares/validateSignupActivation'
import type { CustomRouteGroup } from './types'
import { mustBeUnauthenticated } from './utils'

const NavigateWithParams = ({ to, ...props }: NavigateProps) => {
  const params = useParams()
  return <Navigate {...props} to={generatePath(to as string, params)} />
}

export const routesSignup: CustomRouteGroup['children'] = [
  {
    index: true,
    element: <Navigate to="/bienvenue" />,
    loader: withUserPermissions(mustBeUnauthenticated),
  },
  {
    lazy: async () => ({
      Component: (
        await import('@/pages/Signup/SignupContainer/SignupContainer')
      ).SignupContainer,
    }),
    loader: noop,
    path: 'compte/creation',
    handle: {
      title: 'Créer un compte',
    },
  },
  {
    lazy: async () => ({
      Component: (
        await import('@/pages/Signup/SignupConfirmation/SignupConfirmation')
      ).SignupConfirmation,
    }),
    loader: noop,
    path: 'compte/confirmation',
    handle: {
      title: 'Validez votre adresse email',
    },
  },
  {
    element: null,
    loader: withUserPermissions(() => true, validateSignupActivation),
    path: 'compte/confirmation/:token',
    handle: {
      title: 'Confirmation de création de compte',
    },
  },
  // Redirects until pages are changed in organization website
  {
    element: (
      <NavigateWithParams to="/inscription/compte/confirmation/:token" />
    ),
    loader: noop,
    path: 'validation/:token',
    handle: {
      title: 'Confirmation de création de compte',
    },
  },
  {
    element: <Navigate to="/inscription/compte/confirmation" />,
    loader: noop,
    path: 'confirmation',
    handle: {
      title: 'Confirmation de création de compte',
    },
  },
]
