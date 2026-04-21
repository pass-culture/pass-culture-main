/* No need to test this file */
/* istanbul ignore file */

import { noop } from '@/commons/utils/noop'

import type { CustomRouteGroupChild } from './types'

export const routesEcoDesign: CustomRouteGroupChild[] = [
  {
    lazy: () => import('@/pages/EcoDesign/EcoDesignMenu'),
    loader: noop,
    path: '',
    title: 'Déclaration d\u2019écoconception de l\u2019espace partenaires',
  },
  {
    lazy: () => import('@/pages/EcoDesign/Policy'),
    loader: noop,
    path: 'politique',
    title: "Politique d'écoconception au pass Culture",
  },
  {
    lazy: () => import('@/pages/EcoDesign/Declaration'),
    loader: noop,
    path: 'declaration',
    title: 'Déclaration RGESN',
  },
]
