import React, { FunctionComponent } from 'react'

import { DisplayInAppLink } from 'new_components/DisplayInAppLink'
import { WEBAPP_URL } from 'utils/config'

type Props = {
  nonHumanizedId: number
  children?: never
}

export const DisplayOfferInAppLink: FunctionComponent<Props> = ({
  nonHumanizedId,
}) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${nonHumanizedId}`

  return (
    <DisplayInAppLink
      className="secondary-link"
      link={offerPreviewUrl}
      trackOffer
    >
      Visualiser dans l’app
    </DisplayInAppLink>
  )
}
