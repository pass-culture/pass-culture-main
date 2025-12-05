import type React from 'react'
import type { FunctionComponent } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { WEBAPP_URL } from '@/commons/utils/config'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import type { SharedButtonProps } from '@/ui-kit/Button/types'

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
  const { logEvent } = useAnalytics()

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
        logEvent(Events.CLICKED_VIEW_APP_OFFER, {
          offerId: id,
          from: location.pathname,
        })
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
