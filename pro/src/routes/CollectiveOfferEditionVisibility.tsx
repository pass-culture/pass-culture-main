import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import React from 'react'

const CollectiveOfferVisibility = () => {
  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer={false}
      title="Editer une offre collective"
    >
      <CollectiveOfferVisibilityScreen />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
