/* No need to test this file */
/* istanbul ignore file */
import React from 'react'

import SignupConfirmation from 'deprecatedPages/Signup/SignupConfirmation/SignupConfirmation'
import SignupContainer from 'deprecatedPages/Signup/SignupContainer/SignupContainer'
import SignUpValidation from 'deprecatedPages/Signup/SignUpValidation'

import type { IRoute } from './routesMap'

export const routesSignup: IRoute[] = [
  {
    element: <SignupContainer />,
    parentPath: '/inscription',
    path: '/',
    title: 'S’inscrire',
  },
  {
    element: <SignupConfirmation />,
    parentPath: '/inscription',
    path: '/confirmation',
    title: 'S’inscrire',
  },
  {
    element: <SignUpValidation />,
    parentPath: '/inscription',
    path: '/validation/:token',
    title: 'S’inscrire',
  },
]

export default routesSignup
