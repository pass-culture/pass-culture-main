import type { FunctionComponent } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { WEBAPP_URL } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import type { ButtonAsLinkProps } from '@/design-system/Button/types'

interface DisplayOfferInAppLinkProps
  extends Partial<Omit<ButtonAsLinkProps, 'id'>> {
  id: number
  onClick?: () => void
}

export const DisplayOfferInAppLink: FunctionComponent<
  DisplayOfferInAppLinkProps
> = ({ id, onClick, ...originalProps }) => {
  const offerPreviewUrl = `${WEBAPP_URL}/offre/${id}`
  const { logEvent } = useAnalytics()

  return (
    <Button
      {...originalProps}
      as="a"
      to={offerPreviewUrl}
      isExternal
      onClick={() => {
        logEvent(Events.CLICKED_VIEW_APP_OFFER, {
          offerId: id,
        })
        onClick?.()
      }}
      opensInNewTab
    />
  )
}
