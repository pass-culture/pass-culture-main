import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { OFFER_FORM_STEP_IDS, fakeOffer } from '../constants'

import { ActionBar } from '../ActionBar'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import React from 'react'
import { getStepsOffer } from '../utils/steps'
import { useHistory } from 'react-router-dom'

const Summary = (): JSX.Element => {
  const history = useHistory()
  const { stepList } = getStepsOffer(fakeOffer)
  const handleNextStep = () => {
    // TODO get offerId from url query string
    history.push(`/offre/${fakeOffer.id}/v3/creation/individuelle/confirmation`)
  }
  const handlePreviousStep = () => {
    // TODO get offerId from url query string
    history.push(`/offre/${fakeOffer.id}/v3/creation/individuelle/stocks`)
  }

  return (
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock>
        <h1>Créer une offe</h1>
      </OfferFormLayout.TitleBlock>

      <OfferFormLayout.Stepper>
        <Breadcrumb
          activeStep={OFFER_FORM_STEP_IDS.SUMMARY}
          steps={Object.values(stepList)}
          styleType={BreadcrumbStyle.TAB}
        />
      </OfferFormLayout.Stepper>

      <OfferFormLayout.Content>
        <h2>Récapitulatif</h2>

        <p> TODO Récapitulatif </p>
        <p> TODO app preview sidebar </p>

        <OfferFormLayout.ActionBar>
          <ActionBar
            onClickNext={handleNextStep}
            onClickPrevious={handlePreviousStep}
          />
        </OfferFormLayout.ActionBar>
      </OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default Summary
