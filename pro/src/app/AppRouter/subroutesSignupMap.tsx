/* No need to test this file */
/* istanbul ignore file */

import {
  generatePath,
  Navigate,
  type NavigateProps,
  useParams,
} from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { noop } from '@/commons/utils/noop'
import { SignupValidation } from '@/pages/Signup/SignUpValidation/SignUpValidation'
import { SignupConfirmation } from '@/pages/Signup/SignupConfirmation/SignupConfirmation'
import { SignupContainer } from '@/pages/Signup/SignupContainer/SignupContainer'

import type { CustomRouteGroupChild } from './types'
import { mustBeUnauthenticated } from './utils'

const NavigateWithParams = ({ to, ...props }: NavigateProps) => {
  const params = useParams()
  return <Navigate {...props} to={generatePath(to as string, params)} />
}

export const routesSignup: CustomRouteGroupChild[] = [
  {
    path: '/inscription',
    element: <Navigate to="/bienvenue" />,
    loader: withUserPermissions(mustBeUnauthenticated),
  },
  {
    element: <SignupContainer />,
    loader: noop,
    path: '/inscription/compte/creation',
    handle: {
      title: 'Créer un compte',
    },
  },
  {
    element: <SignupConfirmation />,
    loader: noop,
    path: '/inscription/compte/confirmation',
    handle: {
      title: 'Validez votre adresse email',
    },
  },
  {
    element: <SignupValidation />,
    // fix loader double call first
    // loader: withUserPermissions(() => true, validateSignupActivation),
    loader: noop,
    path: '/inscription/compte/confirmation/:token',
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
    path: '/inscription/validation/:token',
    handle: {
      title: 'Confirmation de création de compte',
    },
  },
  {
    element: <Navigate to="/inscription/compte/confirmation" />,
    loader: noop,
    path: '/inscription/confirmation',
    handle: {
      title: 'Confirmation de création de compte',
    },
  },
]
