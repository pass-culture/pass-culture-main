import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import {
  EducationalInstitutionResponseModel,
  GetCollectiveOfferResponseModel,
} from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  Mode,
  extractOfferIdAndOfferTypeFromRouteParams,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { getCollectiveStockAdapter } from 'core/OfferEducational/adapters/getCollectiveStockAdapter'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

const CollectiveOfferVisibility = () => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const notify = useNotification()

  const [isEditable, setIsEditable] = useState<boolean>()
  const [institution, setInstitution] =
    useState<EducationalInstitutionResponseModel | null>()
  const [institutions, setInstitutions] = useState<
    EducationalInstitutionResponseModel[]
  >([])
  const [isReady, setIsReady] = useState(false)
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(true)

  useEffect(() => {
    Promise.all([
      getCollectiveStockAdapter({ offerId }),
      getCollectiveOfferAdapter(offerId),
    ]).then(([stockResult, offerResult]) => {
      if (!stockResult.isOk || !offerResult.isOk) {
        return notify.error(stockResult.message)
      }

      setInstitution(offerResult.payload.institution)
      setIsEditable(stockResult.payload?.stock?.isEducationalStockEditable)
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
    payload: GetCollectiveOfferResponseModel
  }) => {
    setInstitution(payload.institution)
    notify.success(message)
  }

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer={false}
      title="Éditer une offre collective"
      offerId={offerId}
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
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
