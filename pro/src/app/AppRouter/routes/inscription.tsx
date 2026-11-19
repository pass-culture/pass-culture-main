import {
  generatePath,
  Navigate,
  type NavigateProps,
  useParams,
} from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { noop } from '@/commons/utils/noop'
import { SignupConfirmation } from '@/pages/Signup/SignupConfirmation/SignupConfirmation'
import { SignupContainer } from '@/pages/Signup/SignupContainer/SignupContainer'

import { validateSignupActivation } from '../middlewares/validateSignupActivation'
import type { CustomRouteGroup } from '../types'
import { mustBeUnauthenticated } from '../utils'

export const INSCRIPTION_ROUTES = {
  INSCRIPTION: '/inscription',
  INSCRIPTION_COMPTE_CREATION: '/inscription/compte/creation',
  INSCRIPTION_COMPTE_CONFIRMATION: '/inscription/compte/confirmation',
  INSCRIPTION_COMPTE_CONFIRMATION_TOKEN:
    '/inscription/compte/confirmation/:token',
  INSCRIPTION_VALIDATION_TOKEN: '/inscription/validation/:token',
  INSCRIPTION_CONFIRMATION: '/inscription/confirmation',
} as const

const NavigateWithParams = ({ to, ...props }: NavigateProps) => {
  const params = useParams()
  return <Navigate {...props} to={generatePath(to as string, params)} />
}

export const inscriptionRoutes: CustomRouteGroup['children'] = [
  {
    index: true,
    element: <Navigate to="/bienvenue" />,
    loader: withUserPermissions(mustBeUnauthenticated),
  },
  {
    element: <SignupContainer />,
    loader: noop,
    path: 'compte/creation',
    handle: {
      title: 'Créer un compte',
    },
  },
  {
    element: <SignupConfirmation />,
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
