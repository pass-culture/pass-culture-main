import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import React from 'react'

const CollectiveOfferVisibility = () => {
  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer
      title="Créer une nouvelle offre collective"
    >
      <CollectiveOfferVisibilityScreen />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
