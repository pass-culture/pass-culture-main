import { redirect } from 'react-router'

import type { RedirectionRouteObject } from './types'

export const redirectedRoutes: RedirectionRouteObject[] = [
  {
    path: '/offre/individuelle/:offerId/recapitulatif',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/recapitulatif/details`),
  },
  {
    path: '/offre/individuelle/:offerId/recapitulatif/details',
    loader: ({ params }) =>
      redirect(
        `/offre/individuelle/${params.offerId}/recapitulatif/description`
      ),
  },
]
