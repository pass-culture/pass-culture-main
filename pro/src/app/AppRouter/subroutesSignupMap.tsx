/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import { SignupConfirmation } from 'pages/Signup/SignupConfirmation/SignupConfirmation'
import { SignupContainer } from 'pages/Signup/SignupContainer/SignupContainer'
import { SignupValidation } from 'pages/Signup/SignUpValidation/SignUpValidation'

import type { RouteConfig } from './routesMap'

export const routesSignup: RouteConfig[] = [
  {
    element: <SignupContainer />,
    path: '/inscription',
    title: 'Créer un compte',
    meta: { public: true },
  },
  {
    element: <SignupConfirmation />,
    path: '/inscription/confirmation',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
  {
    element: <SignupValidation />,
    path: '/inscription/validation/:token',
    title: 'Confirmation de création de compte',
    meta: { public: true },
  },
]
