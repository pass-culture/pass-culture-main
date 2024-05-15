import React from 'react'

import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { FormLayoutDescription } from 'components/FormLayout/FormLayoutDescription'
import { isOfferDisabled } from 'core/Offers/utils/isOfferDisabled'

interface EventCancellationBannerProps {
  offer: GetIndividualOfferResponseModel
}

export const EventCancellationBanner = ({
  offer,
}: EventCancellationBannerProps) =>
  !isOfferDisabled(offer.status) ? (
    <FormLayoutDescription
      description="Les bénéficiaires ont 48h pour annuler leur réservation. Ils ne peuvent pas le faire à moins de 48h de l’évènement.
      Vous pouvez annuler un évènement en supprimant la ligne de stock associée. Cette action est irréversible."
      links={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/4411992053649--Acteurs-Culturels-Comment-annuler-ou-reporter-un-%C3%A9v%C3%A9nement-',
          label: 'Comment reporter ou annuler un évènement ?',
          isExternal: true,
        },
      ]}
      isBanner
    />
  ) : null
