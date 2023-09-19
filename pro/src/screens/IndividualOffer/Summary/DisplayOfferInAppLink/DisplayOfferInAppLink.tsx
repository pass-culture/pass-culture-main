import React, { FunctionComponent } from 'react'

import { ButtonLinkNewWindow } from 'components/ButtonLinkNewWindow'
import { SharedButtonProps } from 'ui-kit/Button/types'
import { WEBAPP_URL } from 'utils/config'

interface DisplayOfferInAppLinkProps extends SharedButtonProps {
  id: number
  tracking?: { isTracked: boolean; trackingFunction: () => void }
  text?: string
  icon?: string
  svgAlt?: string
}

export const DisplayOfferInAppLink: FunctionComponent<
  DisplayOfferInAppLinkProps
> = ({ id, tracking, icon, variant, text, svgAlt }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${id}`

  return (
    <ButtonLinkNewWindow
      linkTo={offerPreviewUrl}
      tracking={tracking}
      variant={variant}
      icon={icon}
      svgAlt={svgAlt}
    >
      {text ? text : 'Visualiser dans l’app'}
    </ButtonLinkNewWindow>
  )
}
