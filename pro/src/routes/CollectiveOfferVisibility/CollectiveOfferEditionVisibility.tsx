import { EducationalInstitution, Mode } from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'

import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
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

  useEffect(() => {
    Promise.all([
      getCollectiveStockAdapter({ offerId }),
      getCollectiveOfferAdapter(offerId),
    ]).then(([stockResult, offerResult]) => {
      if (!stockResult.isOk || !offerResult.isOk) {
        return notify.error(stockResult.message)
      }

      setIsEditable(stockResult.payload?.stock?.isEducationalStockEditable)
      setInstitution(offerResult.payload.institution)
    })
  }, [])

  const onSuccess = ({ message }: { message: string }) => {
    notify.success(message)
  }

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer={false}
      title="Editer une offre collective"
      offerId={offerId}
    >
      <CollectiveOfferVisibilityScreen
        getInstitutions={getEducationalInstitutionsAdapter}
        mode={isEditable ? Mode.EDITION : Mode.READ_ONLY}
        patchInstitution={patchEducationalInstitutionAdapter}
        initialValues={{
          institution: institution?.id?.toString() ?? '',
          'search-institution': institution?.name ?? '',
          visibility: institution ? 'one' : 'all',
        }}
        onSuccess={onSuccess}
      />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
