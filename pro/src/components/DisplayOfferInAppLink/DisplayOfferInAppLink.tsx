import { WEBAPP_URL } from 'commons/utils/config'
import React, { FunctionComponent } from 'react'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SharedButtonProps } from 'ui-kit/Button/types'

interface DisplayOfferInAppLinkProps extends SharedButtonProps {
  id: number
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

export const DisplayOfferInAppLink: FunctionComponent<
  DisplayOfferInAppLinkProps
> = ({ id, icon, iconAlt, children, variant, onClick, className }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${id}`

  return (
    <ButtonLink
      to={offerPreviewUrl}
      isExternal
      variant={variant}
      icon={icon}
      iconAlt={iconAlt}
      className={className}
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
