import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { Mode } from 'core/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import React from 'react'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

const CollectiveOfferVisibility = () => {
  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer={false}
      title="Editer une offre collective"
    >
      <CollectiveOfferVisibilityScreen
        getInstitutions={getEducationalInstitutionsAdapter}
        mode={Mode.EDITION}
        patchInstitution={patchEducationalInstitutionAdapter}
      />
      <RouteLeavingGuardOfferCreation isCollectiveFlow />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
