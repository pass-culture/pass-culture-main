import React from 'react'
import { useHistory } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { Mode, CollectiveOffer } from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { useAdapter } from 'hooks'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

const CollectiveOfferVisibility = ({ offer }: { offer: CollectiveOffer }) => {
  const notify = useNotification()
  const history = useHistory()

  const {
    error,
    data: institutionsPayload,
    isLoading,
  } = useAdapter(getEducationalInstitutionsAdapter)

  const onSuccess = ({
    message,
    payload,
  }: {
    message: string
    payload: CollectiveOffer
  }) => {
    notify.success(message)
    history.push(
      `/offre/${computeURLCollectiveOfferId(
        payload.id,
        false
      )}/collectif/recapitulatif`
    )
  }

  if (isLoading) {
    return <Spinner />
  }

  if (error) {
    return null
  }

  return (
    <CollectiveOfferVisibilityScreen
      mode={offer.isVisibilityEditable ? Mode.EDITION : Mode.READ_ONLY}
      patchInstitution={patchEducationalInstitutionAdapter}
      initialValues={extractInitialVisibilityValues(offer.institution)}
      onSuccess={onSuccess}
      institutions={institutionsPayload.institutions}
      isLoadingInstitutions={isLoading}
    />
  )
}

export default CollectiveOfferVisibility
