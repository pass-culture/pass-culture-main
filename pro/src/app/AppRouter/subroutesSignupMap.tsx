/* No need to test this file */
/* istanbul ignore file */

import {
  generatePath,
  Navigate,
  type NavigateProps,
  useParams,
} from 'react-router'

import { noop } from '@/commons/utils/noop'
import { SignupValidation } from '@/pages/Signup/SignUpValidation/SignUpValidation'
import { SignupConfirmation } from '@/pages/Signup/SignupConfirmation/SignupConfirmation'
import { SignupContainer } from '@/pages/Signup/SignupContainer/SignupContainer'

import type { CustomRouteObject } from './types'

const NavigateWithParams = ({ to, ...props }: NavigateProps) => {
  const params = useParams()
  return <Navigate {...props} to={generatePath(to as string, params)} />
}

export const routesSignup: CustomRouteObject[] = [
  {
    element: <SignupContainer />,
    loader: noop,
    path: '/inscription/compte/creation',
    title: 'Créer un compte',
    meta: { public: true },
  },
  {
    element: <SignupConfirmation />,
    loader: noop,
    path: '/inscription/compte/confirmation',
    title: 'Validez votre adresse email',
    meta: { public: true },
  },
  {
    element: <SignupValidation />,
    loader: noop,
    path: '/inscription/compte/confirmation/:token',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },

  // Redirects until pages are changed in organization website
  {
    element: (
      <NavigateWithParams to="/inscription/compte/confirmation/:token" />
    ),
    loader: noop,
    path: '/inscription/validation/:token',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
  {
    element: <Navigate to="/inscription/compte/confirmation" />,
    loader: noop,
    path: '/inscription/confirmation',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
  {
    element: <Navigate to="/inscription/compte/creation" />,
    loader: noop,
    path: '/inscription',
    title: 'Créer un compte',
    meta: { public: true },
  },
]
