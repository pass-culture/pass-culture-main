import type { FunctionComponent } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { WEBAPP_URL } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import type { ButtonProps } from '@/design-system/Button/types'

type ButtonLinkProps = Partial<Omit<ButtonProps, 'id'>>
interface DisplayOfferInAppLinkProps extends ButtonLinkProps {
  id: number
  onClick?: () => void
  className?: string
}

export const DisplayOfferInAppLink: FunctionComponent<
  DisplayOfferInAppLinkProps
> = ({ id, label, icon, iconAlt, variant, onClick, fullWidth }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${id}`
  const { logEvent } = useAnalytics()

  return (
    <Button
      as="a"
      label={label}
      to={offerPreviewUrl}
      isExternal
      variant={variant}
      icon={icon}
      iconAlt={iconAlt}
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
      fullWidth={fullWidth}
    />
  )
}
