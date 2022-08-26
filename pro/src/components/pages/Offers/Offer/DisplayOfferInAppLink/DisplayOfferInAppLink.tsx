import React, { FunctionComponent } from 'react'

import Icon from 'components/layout/Icon'
import { DisplayInAppLink } from 'new_components/DisplayInAppLink'
import { WEBAPP_URL } from 'utils/config'

type Props = {
  nonHumanizedId: number
  children?: never
  isTertiary?: boolean
  tracking?: { isTracked: boolean; trackingFunction: () => void }
}

export const DisplayOfferInAppLink: FunctionComponent<Props> = ({
  nonHumanizedId,
  isTertiary,
  tracking,
}) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${nonHumanizedId}`

  return (
    <DisplayInAppLink
      className={isTertiary ? 'tertiary-link' : 'secondary-link'}
      link={offerPreviewUrl}
      tracking={tracking}
    >
      {isTertiary && <Icon svg={'ico-external-site-filled'} />}
      Visualiser dans l’app
    </DisplayInAppLink>
  )
}
