import React from 'react'
import { useLocation, Route, Routes, useParams } from 'react-router-dom'

import { routesIndividualOfferWizard } from 'app/AppRouter/subroutesIndividualOfferWizardMap'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

const IndividualOfferWizard = () => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId, 'sous-categorie': querySubcategoryId } =
    parse(search)

  return (
    <IndividualOfferContextProvider
      isUserAdmin={currentUser.isAdmin}
      offerId={offerId === 'creation' ? undefined : offerId}
      queryOffererId={offererId}
      querySubcategoryId={querySubcategoryId}
    >
      <Routes>
        {routesIndividualOfferWizard.map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
      </Routes>
    </IndividualOfferContextProvider>
  )
}

export default IndividualOfferWizard
