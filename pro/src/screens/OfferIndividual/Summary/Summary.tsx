import { useHistory, useLocation } from 'react-router-dom'

import { ActionBar } from '../ActionBar'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { IOfferIndividual } from 'core/Offers/types'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'

interface ISummaryProps {
  formOfferV2?: boolean
  isCreation?: boolean
  offer: IOfferIndividual
}

const Summary = ({
  formOfferV2 = false,
  isCreation = false,
  offer,
}: ISummaryProps): JSX.Element => {
  const location = useLocation()
  const history = useHistory()
  const handleNextStep = () => {
    history.push(`/offre/${offer.id}/v3/creation/individuelle/confirmation`)
  }
  const handlePreviousStep = () => {
    history.push(`/offre/${offer.id}/v3/creation/individuelle/stocks`)
  }

  return (
    <>
      <h2>Récapitulatif</h2>

      <p> TODO Récapitulatif </p>
      <p> TODO app preview sidebar </p>
      {formOfferV2 ? (
        isCreation && (
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            to={`/offre/${offer.id}/individuel/creation/confirmation${location.search}`}
          >
            Publier
          </ButtonLink>
        )
      ) : (
        <OfferFormLayout.ActionBar>
          <ActionBar
            onClickNext={handleNextStep}
            onClickPrevious={handlePreviousStep}
          />
        </OfferFormLayout.ActionBar>
      )}
    </>
  )
}

export default Summary
