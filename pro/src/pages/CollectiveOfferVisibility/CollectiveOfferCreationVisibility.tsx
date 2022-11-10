import React, { useEffect, useState } from 'react'
import { useHistory } from 'react-router'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import RouteLeavingGuardOfferCreation from 'components/RouteLeavingGuardOfferCreation'
import {
  CollectiveOffer,
  DEFAULT_VISIBILITY_FORM_VALUES,
  Mode,
} from 'core/OfferEducational'
import { extractInitialVisibilityValues } from 'core/OfferEducational/utils/extractInitialVisibilityValues'
import CollectiveOfferVisibilityScreen from 'screens/CollectiveOfferVisibility'

import getEducationalInstitutionsAdapter from './adapters/getEducationalInstitutionsAdapter'
import patchEducationalInstitutionAdapter from './adapters/patchEducationalInstitutionAdapter'

interface CollectiveOfferVisibilityProps {
  setOffer: (offer: CollectiveOffer) => void
  isDuplicatingOffer?: boolean
  offer: CollectiveOffer
}

const CollectiveOfferVisibility = ({
  setOffer,
  isDuplicatingOffer = false,
  offer,
}: CollectiveOfferVisibilityProps) => {
  const history = useHistory()

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
    const successUrl = isDuplicatingOffer
      ? `/offre/duplication/collectif/${offerId}/recapitulatif`
      : `/offre/${offerId}/collectif/creation/recapitulatif`
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

  const initialValues = offer
    ? extractInitialVisibilityValues(offer.institution)
    : DEFAULT_VISIBILITY_FORM_VALUES
  return (
    <>
      <CollectiveOfferVisibilityScreen
        mode={Mode.CREATION}
        patchInstitution={patchEducationalInstitutionAdapter}
        initialValues={initialValues}
        onSuccess={onSuccess}
        institutions={institutions}
        isLoadingInstitutions={isLoadingInstitutions}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferVisibility
