import React from 'react'
import { useLocation } from 'react-router'
import { Route, Routes, useParams } from 'react-router-dom-v5-compat'

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
          '/informations',
          '/creation/informations',
          '/brouillon/informations',
          '/informations',
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

        {['/creation/tarifs', '/brouillon/tarifs', '/tarifs'].map(
          (path: string) => (
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
          )
        )}

        {['/creation/stocks', '/brouillon/stocks', '/stocks'].map(
          (path: string) => (
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
          )
        )}

        {[
          '/creation/recapitulatif',
          '/brouillon/recapitulatif',
          '/recapitulatif',
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
          '/creation/confirmation',
          '/brouillon/confirmation',
          '/confirmation',
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
