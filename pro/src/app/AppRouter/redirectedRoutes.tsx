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
  // TODO (rchaffal) 6/07/2026: Page Exposure you can remove these redirections in six months
  {
    path: '/offre/individuelle/:offerId/recapitulatif/description',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/edition/description`),
  },
  {
    path: '/offre/individuelle/:offerId/localisation',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/edition/localisation`),
  },
  {
    path: '/offre/individuelle/:offerId/media',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/edition/media`),
  },
  {
    path: '/offre/individuelle/:offerId/tarifs',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/edition/tarifs`),
  },
  {
    path: '/offre/individuelle/:offerId/horaires',
    loader: ({ params }) =>
      redirect(`/offre/individuelle/${params.offerId}/edition/horaires`),
  },
  {
    path: '/offre/individuelle/:offerId/informations_pratiques',
    loader: ({ params }) =>
      redirect(
        `/offre/individuelle/${params.offerId}/edition/informations_pratiques`
      ),
  },
]
