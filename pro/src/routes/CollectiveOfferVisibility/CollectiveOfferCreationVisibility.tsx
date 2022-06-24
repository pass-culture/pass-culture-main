import {
  DEFAULT_VISIBILITY_FORM_VALUES,
  EducationalInstitution,
  Mode,
} from 'core/OfferEducational'
import React, { useEffect, useState } from 'react'

import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'
import { useHistory } from 'react-router'

const CollectiveOfferVisibility = () => {
  const history = useHistory()

  const [institutions, setInstitutions] = useState<EducationalInstitution[]>([])
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(true)

  const onSuccess = ({ offerId }: { offerId: string }) => {
    const successUrl = `/offre/${offerId}/collectif/confirmation`
    history.push(successUrl)
  }

  useEffect(() => {
    getEducationalInstitutionsAdapter().then(result => {
      if (result.isOk) {
        setInstitutions(result.payload.institutions)
        setIsLoadingInstitutions(false)
      }
    })
  }, [])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.VISIBILITY}
      isCreatingOffer
      title="Créer une nouvelle offre collective"
    >
      <CollectiveOfferVisibilityScreen
        mode={Mode.CREATION}
        patchInstitution={patchEducationalInstitutionAdapter}
        initialValues={DEFAULT_VISIBILITY_FORM_VALUES}
        onSuccess={onSuccess}
        institutions={institutions}
        isLoadingInstitutions={isLoadingInstitutions}
      />
      <RouteLeavingGuardOfferCreation isCollectiveFlow />
    </OfferEducationalLayout>
  )
}

export default CollectiveOfferVisibility
