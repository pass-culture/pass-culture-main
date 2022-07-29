import React from 'react'
import { useParams } from 'react-router'

import Titles from 'components/layout/Titles/Titles'
import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

const OfferIndividualEdition = (): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()
  return (
    <div>
      <Titles title="Editez votre offre" />
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

export default OfferIndividualEdition
