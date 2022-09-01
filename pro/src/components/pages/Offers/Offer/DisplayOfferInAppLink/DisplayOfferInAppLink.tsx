import React, { FunctionComponent } from 'react'

import { ButtonLinkNewWindow } from 'new_components/ButtonLinkNewWindow'
import { SharedButtonProps } from 'ui-kit/Button/types'
import { WEBAPP_URL } from 'utils/config'

interface IDisplayOfferInAppLinkProps extends SharedButtonProps {
  nonHumanizedId: number
  tracking?: { isTracked: boolean; trackingFunction: () => void }
  text?: string
}

export const DisplayOfferInAppLink: FunctionComponent<
  IDisplayOfferInAppLinkProps
> = ({ nonHumanizedId, tracking, Icon, variant, text }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${nonHumanizedId}`

  return (
    <ButtonLinkNewWindow
      linkTo={offerPreviewUrl}
      tracking={tracking}
      variant={variant}
      Icon={Icon}
    >
      {text ? text : 'Visualiser dans l’app'}
    </ButtonLinkNewWindow>
  )
}
