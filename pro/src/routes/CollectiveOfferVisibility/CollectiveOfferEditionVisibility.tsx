import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  Mode,
  extractOfferIdAndOfferTypeFromRouteParams,
  CollectiveOffer,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

const CollectiveOfferVisibility = () => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const notify = useNotification()
  const history = useHistory()

  const [institutions, setInstitutions] = useState<
    EducationalInstitutionResponseModel[]
  >([])
  const [isReady, setIsReady] = useState(false)
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(true)
  const [offer, setOffer] = useState<CollectiveOffer>()

  useEffect(() => {
    getCollectiveOfferAdapter(offerId).then(offerResult => {
      if (!offerResult.isOk) {
        return notify.error(offerResult.message)
      }

      setOffer(offerResult.payload)
      setIsReady(true)
    })
  }, [])

  useEffect(() => {
    getEducationalInstitutionsAdapter().then(result => {
      if (!result.isOk) {
        return notify.error(result.message)
      }

      setInstitutions(result.payload.institutions)
      setIsLoadingInstitutions(false)
    })
  }, [])

  const onSuccess = ({
    message,
    payload,
  }: {
    message: string
    payload: CollectiveOffer
  }) => {
    setOffer(currentOffer => {
      if (!currentOffer) {
        return
      }
      return { ...currentOffer, institution: payload.institution }
    })

    notify.success(message)
    history.push(
      `/offre/${computeURLCollectiveOfferId(
        payload.id,
        false
      )}/collectif/recapitulatif`
    )
  }

  if (!isReady || !offer) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.VISIBILITY,
        isCreatingOffer: false,
        offerId,
      }}
      title="Éditer une offre collective"
      subTitle={offer.name}
    >
      <CollectiveOfferVisibilityScreen
        mode={offer.isVisibilityEditable ? Mode.EDITION : Mode.READ_ONLY}
        patchInstitution={patchEducationalInstitutionAdapter}
        initialValues={extractInitialVisibilityValues(offer.institution)}
        onSuccess={onSuccess}
        institutions={institutions}
        isLoadingInstitutions={isLoadingInstitutions}
      />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferVisibility
