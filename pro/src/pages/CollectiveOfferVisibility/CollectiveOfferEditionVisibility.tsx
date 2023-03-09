import React from 'react'
import { useHistory } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  Mode,
  CollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import Spinner from 'ui-kit/Spinner/Spinner'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

const CollectiveOfferVisibility = ({
  offer,
  reloadCollectiveOffer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const notify = useNotification()
  const history = useHistory()
  const {
    error,
    data: institutionsPayload,
    isLoading,
  } = useAdapter(getEducationalInstitutionsAdapter)

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error(
      "Impossible de mettre à jour la visibilité d'une offre vitrine."
    )
  }

  const onSuccess = ({
    message,
    payload,
  }: {
    message: string
    payload: CollectiveOffer
  }) => {
    notify.success(message)
    reloadCollectiveOffer()
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
    <CollectiveOfferLayout subTitle={offer.name}>
      <PageTitle title="Visibilité" />
      <CollectiveOfferVisibilityScreen
        mode={offer.isVisibilityEditable ? Mode.EDITION : Mode.READ_ONLY}
        patchInstitution={patchEducationalInstitutionAdapter}
        initialValues={extractInitialVisibilityValues(
          offer.institution,
          offer.teacher
        )}
        onSuccess={onSuccess}
        institutions={institutionsPayload.institutions}
        isLoadingInstitutions={isLoading}
        offer={offer}
      />
    </CollectiveOfferLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferVisibility)
