

import React from 'react'
import { useHistory } from 'react-router-dom'

import { OfferFormLayout } from 'new_components/OfferFormLayout'

import { ActionBar } from '../ActionBar'
import { fakeOffer } from '../constants'

const Summary = (): JSX.Element => {
  const history = useHistory()
  const handleNextStep = () => {
    // TODO get offerId from url query string
    history.push(`/offre/${fakeOffer.id}/v3/creation/individuelle/confirmation`)
  }
  const handlePreviousStep = () => {
    // TODO get offerId from url query string
    history.push(`/offre/${fakeOffer.id}/v3/creation/individuelle/stocks`)
  }

  return (
    <>
      <h2>Récapitulatif</h2>

      <p> TODO Récapitulatif </p>
      <p> TODO app preview sidebar </p>

      <OfferFormLayout.ActionBar>
        <ActionBar
          onClickNext={handleNextStep}
          onClickPrevious={handlePreviousStep}
        />
      </OfferFormLayout.ActionBar>
    </>
  )
}

export default Summary
