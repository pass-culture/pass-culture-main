import {
  IPayloadFailure,
  IPayloadSuccess,
  getCollectiveStockAdapter,
} from 'routes/OfferEducationalStockEdition/adapters/getCollectiveStockAdapter'
import React, { useEffect, useState } from 'react'

import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { Mode } from 'core/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'
import { useParams } from 'react-router-dom'

const CollectiveOfferVisibility = () => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const [isEditable, setIsEditable] = useState<boolean>()

  useEffect(() => {
    getCollectiveStockAdapter({ offerId }).then(
      (
        result:
          | AdapterSuccess<IPayloadSuccess>
          | AdapterFailure<IPayloadFailure>
      ) => {
        if (result.isOk)
          setIsEditable(result.payload?.stock?.isEducationalStockEditable)
      }
    )
  }, [])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer={false}
      title="Editer une offre collective"
    >
      <CollectiveOfferVisibilityScreen
        getInstitutions={getEducationalInstitutionsAdapter}
        mode={isEditable ? Mode.EDITION : Mode.READ_ONLY}
        patchInstitution={patchEducationalInstitutionAdapter}
      />
      <RouteLeavingGuardOfferCreation isCollectiveFlow />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
