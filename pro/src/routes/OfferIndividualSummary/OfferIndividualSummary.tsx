import { matchPath, useHistory, useLocation, useParams } from 'react-router-dom'

import React from 'react'
import Spinner from 'components/layout/Spinner'
import { Summary as SummaryScreen } from 'screens/OfferIndividual/Summary'
import { useGetOffer } from 'core/Offers/adapters'
import useNotification from 'components/hooks/useNotification'

interface IOfferIndividualSummaryProps {
  formOfferV2?: boolean
}

const OfferIndividualSummary = ({
  formOfferV2 = false,
}: IOfferIndividualSummaryProps): JSX.Element | null => {
  const notify = useNotification()
  const history = useHistory()
  const location = useLocation()
  const isCreation =
    matchPath(
      location.pathname,
      '/offre/:offer_id/individuel/creation/recapitulatif'
    ) !== null

  const { offerId } = useParams<{ offerId: string }>()
  const { data: offer, isLoading, error } = useGetOffer(offerId)

  if (error !== undefined) {
    notify.error(error.message)
    history.push('/offres')
    return null
  }

  if (isLoading) {
    return <Spinner />
  }

  return (
    <div>
      <SummaryScreen
        formOfferV2={formOfferV2}
        isCreation={isCreation}
        offer={offer}
      />
    </div>
  )
}

export default OfferIndividualSummary
