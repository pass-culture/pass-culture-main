import {
  CollectiveOfferResponseModel,
  EducationalInstitution,
  Mode,
} from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'

import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import Spinner from 'components/layout/Spinner'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { getCollectiveStockAdapter } from 'core/OfferEducational/adapters/getCollectiveStockAdapter'
import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'
import useNotification from 'components/hooks/useNotification'
import { useParams } from 'react-router-dom'

const CollectiveOfferVisibility = () => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const notify = useNotification()

  const [isEditable, setIsEditable] = useState<boolean>()
  const [institution, setInstitution] =
    useState<EducationalInstitution | null>()
  const [institutions, setInstitutions] = useState<EducationalInstitution[]>([])
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
  }, [notify, offerId])

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
    payload: CollectiveOfferResponseModel
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
          initialValues={{
            institution: institution?.id?.toString() ?? '',
            'search-institution': institution?.name ?? '',
            visibility: institution ? 'one' : 'all',
          }}
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
