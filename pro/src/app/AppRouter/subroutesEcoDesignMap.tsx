import { noop } from '@/commons/utils/noop'

import type { CustomRouteGroup } from './types'

export const routesEcoDesign: CustomRouteGroup['children'] = [
  {
    lazy: () => import('@/pages/EcoDesign/EcoDesignMenu'),
    loader: noop,
    index: true,
    handle: {
      title: 'Déclaration d\u2019écoconception de l\u2019espace partenaire',
    },
  },
  {
    lazy: () => import('@/pages/EcoDesign/Policy'),
    loader: noop,
    path: 'politique',
    handle: {
      title: "Politique d'écoconception au pass Culture",
    },
  },
  {
    lazy: () => import('@/pages/EcoDesign/Declaration'),
    loader: noop,
    path: 'declaration',
    handle: {
      title: 'Déclaration RGESN',
    },
  },
]
