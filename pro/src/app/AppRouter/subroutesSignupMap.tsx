/* No need to test this file */
/* istanbul ignore file */

import { generatePath, Navigate, NavigateProps, useParams } from 'react-router'

import { SignupValidation } from '@/pages/Signup/SignUpValidation/SignUpValidation'
import { SignupConfirmation } from '@/pages/Signup/SignupConfirmation/SignupConfirmation'
import { SignupContainer } from '@/pages/Signup/SignupContainer/SignupContainer'

import type { RouteConfig } from './routesMap'

const NavigateWithParams = ({ to, ...props }: NavigateProps) => {
  const params = useParams()
  return <Navigate {...props} to={generatePath(to as string, params)} />
}

export const routesSignup: RouteConfig[] = [
  {
    element: <SignupContainer />,
    path: '/inscription/compte/creation',
    title: 'Créer un compte',
    meta: { public: true },
  },
  {
    element: <SignupConfirmation />,
    path: '/inscription/compte/confirmation',
    title: 'Validez votre adresse email',
    meta: { public: true },
  },
  {
    element: <SignupValidation />,
    path: '/inscription/compte/confirmation/:token',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },

  // Redirects until pages are changed in organization website
  {
    element: (
      <NavigateWithParams to="/inscription/compte/confirmation/:token" />
    ),
    path: '/inscription/validation/:token',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
  {
    element: <Navigate to="/inscription/compte/confirmation" />,
    path: '/inscription/confirmation',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
  {
    element: <Navigate to="/inscription/compte/creation" />,
    path: '/inscription',
    title: 'Créer un compte',
    meta: { public: true },
  },
]
