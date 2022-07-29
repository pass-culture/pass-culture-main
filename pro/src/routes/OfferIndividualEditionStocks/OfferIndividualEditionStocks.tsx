import React from 'react'
import { useParams } from 'react-router'

import Titles from 'components/layout/Titles/Titles'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

const OfferIndividualEditionStocks = (): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()
  return (
    <div>
      <Titles title="Stock et prix" />
      <div>
        <ButtonLink
          to={`/offre/${offerId}/v3/individuelle/recapitulatif`}
          variant={ButtonVariant.SECONDARY}
        >
          Annuler et quitter
        </ButtonLink>
      </div>
    </div>
  )
}

export default OfferIndividualEditionStocks
