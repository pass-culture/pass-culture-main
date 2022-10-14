import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import Spinner from 'components/layout/Spinner'
import { DEFAULT_VISIBILITY_FORM_VALUES, Mode } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

const CollectiveOfferVisibility = () => {
  const history = useHistory()
  const notify = useNotification()
  const { offerId } = useParams<{ offerId: string }>()

  const [institutions, setInstitutions] = useState<
    EducationalInstitutionResponseModel[]
  >([])
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(true)

  const onSuccess = ({ offerId }: { offerId: string }) => {
    const successUrl = `/offre/${offerId}/collectif/confirmation`
    history.push(successUrl)
  }

  const {
    error,
    data: offer,
    isLoading,
  } = useAdapter(() => getCollectiveOfferAdapter(offerId))

  useEffect(() => {
    getEducationalInstitutionsAdapter().then(result => {
      if (result.isOk) {
        setInstitutions(result.payload.institutions)
        setIsLoadingInstitutions(false)
      }
    })
  }, [])

  if (error) {
    notify.error(error.message)
    return null
  }
  if (isLoading) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.VISIBILITY,
        isCreatingOffer: true,
      }}
      title="Créer une offre réservable"
      subTitle={offer.name}
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
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferVisibility
