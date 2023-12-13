/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import SignupConfirmation from 'pages/Signup/SignupConfirmation/SignupConfirmation'
import SignupContainer from 'pages/Signup/SignupContainer/SignupContainer'
import SignUpValidation from 'pages/Signup/SignUpValidation'

import type { RouteConfig } from './routesMap'

export const routesSignup: RouteConfig[] = [
  {
    element: <SignupContainer />,
    parentPath: '/inscription',
    path: '/',
    title: 'Créer un compte',
    meta: { public: true },
  },
  {
    element: <SignupConfirmation />,
    parentPath: '/inscription',
    path: '/confirmation',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
  {
    element: <SignUpValidation />,
    parentPath: '/inscription',
    path: '/validation/:token',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
]

export default routesSignup
