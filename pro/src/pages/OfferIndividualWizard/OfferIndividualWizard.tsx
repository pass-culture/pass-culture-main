import React from 'react'
import { useLocation, Route, Routes, useParams } from 'react-router-dom'

import { routesOfferIndividualWizard } from 'app/AppRouter/subroutesOfferIndividualWizardMap'
import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

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
        {routesOfferIndividualWizard.map(({ path, element }) => (
          <Route key={path} path={path} element={element} />
        ))}
      </Routes>
    </OfferIndividualContextProvider>
  )
}

export default OfferIndividualWizard
