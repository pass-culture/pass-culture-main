import React, { FunctionComponent } from 'react'

import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SharedButtonProps } from 'ui-kit/Button/types'
import { WEBAPP_URL } from 'utils/config'

interface DisplayOfferInAppLinkProps extends SharedButtonProps {
  id: number
  icon?: string
  svgAlt?: string
  children: React.ReactNode
  onClick?: () => void
}

export const DisplayOfferInAppLink: FunctionComponent<
  DisplayOfferInAppLinkProps
> = ({ id, icon, children, variant, svgAlt, onClick }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${id}`

  return (
    <ButtonLink
      link={{ to: offerPreviewUrl, isExternal: true }}
      variant={variant}
      icon={icon}
      svgAlt={svgAlt}
      onClick={(event) => {
        event.preventDefault()
        onClick?.()

        window
          .open(
            offerPreviewUrl,
            'targetWindow',
            'toolbar=no, width=375, height=667'
          )
          ?.focus()

        return false
      }}
    >
      {children}
    </ButtonLink>
  )
}
