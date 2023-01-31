import React from 'react'
import { useLocation, useParams } from 'react-router'
import { Route, Routes } from 'react-router-dom-v5-compat'

import PageTitle from 'components/PageTitle/PageTitle'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

import { Confirmation } from './Confirmation'
import { Offer } from './Offer'
import { PriceCategories } from './PriceCategories'
import { Stocks } from './Stocks'
import { Summary } from './Summary'

const OfferIndividualWizard = () => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)
  return (
    <OfferIndividualContextProvider
      isUserAdmin={currentUser.isAdmin}
      offerId={offerId === 'creation' ? undefined : offerId}
      queryOffererId={offererId}
    >
      <Routes>
        {[
          '/offre/individuelle/creation/informations',
          '/offre/individuelle/:offerId/creation/informations',
          '/offre/individuelle/:offerId/brouillon/informations',
          '/offre/individuelle/:offerId/informations',
        ].map((path: string) => (
          <Route
            key={path}
            path={path}
            element={
              <>
                <PageTitle title="Détails de l'offre" />
                <Offer />
              </>
            }
          />
        ))}

        {[
          '/offre/individuelle/:offerId/creation/tarifs',
          '/offre/individuelle/:offerId/brouillon/tarifs',
          '/offre/individuelle/:offerId/tarifs',
        ].map((path: string) => (
          <Route
            key={path}
            path={path}
            element={
              <>
                <PageTitle title="Vos tarifs" />
                <PriceCategories />
              </>
            }
          />
        ))}

        {[
          '/offre/individuelle/:offerId/creation/stocks',
          '/offre/individuelle/:offerId/brouillon/stocks',
          '/offre/individuelle/:offerId/stocks',
        ].map((path: string) => (
          <Route
            key={path}
            path={path}
            element={
              <>
                <PageTitle title="Vos stocks" />
                <Stocks />
              </>
            }
          />
        ))}

        {[
          '/offre/individuelle/:offerId/creation/recapitulatif',
          '/offre/individuelle/:offerId/brouillon/recapitulatif',
          '/offre/individuelle/:offerId/recapitulatif',
        ].map((path: string) => (
          <Route
            key={path}
            path={path}
            element={
              <>
                <PageTitle title="Récapitulatif" />
                <Summary />
              </>
            }
          />
        ))}

        {[
          '/offre/individuelle/:offerId/creation/confirmation',
          '/offre/individuelle/:offerId/brouillon/confirmation',
          '/offre/individuelle/:offerId/confirmation',
        ].map((path: string) => (
          <Route
            key={path}
            path={path}
            element={
              <>
                <PageTitle title="Confirmation" />
                <Confirmation />
              </>
            }
          />
        ))}
      </Routes>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
