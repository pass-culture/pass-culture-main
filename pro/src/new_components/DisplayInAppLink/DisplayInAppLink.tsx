import React, { FunctionComponent, useCallback, MouseEventHandler } from 'react'
import { useSelector } from 'react-redux'

import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { RootState } from 'store/reducers'

interface Props {
  className?: string
  link: string
  children?: React.ReactNode
  trackOffer?: boolean
}

export const DisplayInAppLink: FunctionComponent<Props> = ({
  className,
  link,
  children,
  trackOffer = false,
}) => {
  const logEvent = useSelector((state: RootState) => state.app.logEvent)
  const openWindow: MouseEventHandler = useCallback(
    event => {
      event.preventDefault()

      window
        .open(link, 'targetWindow', 'toolbar=no,width=375,height=667')
        ?.focus()

      if (trackOffer) {
        logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OfferBreadcrumbStep.CONFIRMATION,
          to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
          used: OFFER_FORM_NAVIGATION_MEDIUM.CONFIRMATION_PREVIEW,
          isEdition: false,
        })
      }
    },
    [link]
  )

  return (
    <a
      className={className}
      href={link}
      onClick={openWindow}
      rel="noopener noreferrer"
      target="_blank"
    >
      {children}
    </a>
  )
}
