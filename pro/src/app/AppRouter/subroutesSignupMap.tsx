/* No need to test this file */
/* istanbul ignore file */

import {
  generatePath,
  Navigate,
  type NavigateProps,
  redirect,
  replace,
  useParams,
} from 'react-router'

import { withUserPermissions } from '@/commons/auth/withUserPermissions'
import { isFeatureActive } from '@/commons/store/features/selectors'
import { rootStore } from '@/commons/store/store'
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
    loader: withUserPermissions(mustBeUnauthenticated, () => {
      const state = rootStore.getState()
      if (isFeatureActive(state, 'WIP_PRE_SIGNUP_INFO')) {
        return redirect('/bienvenue')
      }
      return replace('/inscription/compte/creation')
    }),
  },
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
]
