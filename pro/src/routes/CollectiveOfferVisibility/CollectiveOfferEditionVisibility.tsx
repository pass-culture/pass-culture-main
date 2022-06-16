import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import React from 'react'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'

const CollectiveOfferVisibility = () => {
  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer={false}
      title="Editer une offre collective"
    >
      <CollectiveOfferVisibilityScreen
        getInstitutions={getEducationalInstitutionsAdapter}
      />
      <RouteLeavingGuardOfferCreation isCollectiveFlow />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
