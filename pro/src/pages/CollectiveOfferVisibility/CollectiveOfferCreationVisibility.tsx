import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOffer,
  DEFAULT_VISIBILITY_FORM_VALUES,
  Mode,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

export const CollectiveOfferVisibility = ({
  setOffer,
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  const navigate = useNavigate()
  const location = useLocation()
  const isCreation = !location.pathname.includes('edition')

  const { requete: requestId } = queryParamsFromOfferer(location)
  const [institutions, setInstitutions] = useState<
    EducationalInstitutionResponseModel[]
  >([])
  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(true)
  const onSuccess = ({
    offerId,
    payload,
  }: {
    offerId: string
    payload: CollectiveOffer
  }) => {
    setOffer(payload)
    navigate(`/offre/${offerId}/collectif/creation/recapitulatif`)
  }

  useEffect(() => {
    getEducationalInstitutionsAdapter().then(result => {
      if (result.isOk) {
        setInstitutions(result.payload.institutions)
        setIsLoadingInstitutions(false)
      }
    })
  }, [])

  if (isCollectiveOfferTemplate(offer)) {
    throw new Error(
      "Impossible de mettre à jour la visibilité d'une offre vitrine."
    )
  }

  const initialValues = offer
    ? extractInitialVisibilityValues(offer.institution)
    : DEFAULT_VISIBILITY_FORM_VALUES

  return (
    <CollectiveOfferLayout
      subTitle={offer?.name}
      isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
      isTemplate={isTemplate}
      isCreation={isCreation}
      requestId={requestId}
    >
      <CollectiveOfferVisibilityScreen
        mode={Mode.CREATION}
        patchInstitution={patchEducationalInstitutionAdapter}
        initialValues={initialValues}
        onSuccess={onSuccess}
        institutions={institutions}
        isLoadingInstitutions={isLoadingInstitutions}
        offer={offer}
        requestId={requestId}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </CollectiveOfferLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferVisibility)
