import React, { FunctionComponent } from 'react'

import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SharedButtonProps } from 'ui-kit/Button/types'
import { WEBAPP_URL } from 'utils/config'

interface DisplayOfferInAppLinkProps extends SharedButtonProps {
  id: number
  icon?: string
  children: React.ReactNode
  onClick?: () => void
}

export const DisplayOfferInAppLink: FunctionComponent<
  DisplayOfferInAppLinkProps
> = ({ id, icon, children, variant, onClick }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${id}`

  return (
    <ButtonLink
      to={offerPreviewUrl}
      isExternal
      variant={variant}
      icon={icon}
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
