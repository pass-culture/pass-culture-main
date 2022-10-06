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

  const [isEditable, setIsEditable] = useState<boolean>()
  const [institution, setInstitution] =
    useState<EducationalInstitutionResponseModel | null>()
  const [institutions, setInstitutions] = useState<
    EducationalInstitutionResponseModel[]
  >([])
  const [isReady, setIsReady] = useState(false)
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(true)

  useEffect(() => {
    getCollectiveOfferAdapter(offerId).then(offerResult => {
      if (!offerResult.isOk) {
        return notify.error(offerResult.message)
      }

      setInstitution(offerResult.payload.institution)
      setIsEditable(offerResult.payload.isVisibilityEditable)
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
    setInstitution(payload.institution)
    notify.success(message)
    history.push(
      `/offre/${computeURLCollectiveOfferId(
        payload.id,
        false
      )}/collectif/recapitulatif`
    )
  }

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.VISIBILITY,
        isCreatingOffer: false,
        offerId,
      }}
      title="Éditer une offre collective"
    >
      {isReady ? (
        <CollectiveOfferVisibilityScreen
          mode={isEditable ? Mode.EDITION : Mode.READ_ONLY}
          patchInstitution={patchEducationalInstitutionAdapter}
          initialValues={extractInitialVisibilityValues(institution)}
          onSuccess={onSuccess}
          institutions={institutions}
          isLoadingInstitutions={isLoadingInstitutions}
        />
      ) : (
        <Spinner />
      )}
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferVisibility
