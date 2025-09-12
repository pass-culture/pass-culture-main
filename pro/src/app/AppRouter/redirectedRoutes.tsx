import { type NonIndexRouteObject, redirect } from 'react-router'

export const redirectedRoutes: NonIndexRouteObject[] = [
  {
    path: '/offre/individuelle/:offerId/recapitulatif',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/recapitulatif/details`),
  },
]
