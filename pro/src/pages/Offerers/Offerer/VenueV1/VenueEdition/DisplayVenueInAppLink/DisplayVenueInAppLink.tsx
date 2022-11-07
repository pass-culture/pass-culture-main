import React, { FunctionComponent } from 'react'

import { ButtonLinkNewWindow } from 'components/ButtonLinkNewWindow'
import { ReactComponent as LinkIcon } from 'icons/ico-external-site-red-filled.svg'
import { WEBAPP_URL } from 'utils/config'

import styles from './DisplayVenueInAppLink.module.scss'

interface IDisplayVenueInAppLinkProps {
  nonHumanizedId: number
}

export const DisplayVenueInAppLink: FunctionComponent<
  IDisplayVenueInAppLinkProps
> = ({ nonHumanizedId }) => {
  const venuePreviewUrl = `${WEBAPP_URL}/lieu/${nonHumanizedId}`

  return (
    <ButtonLinkNewWindow
      className={styles['display-venue-link-container']}
      linkTo={venuePreviewUrl}
      Icon={LinkIcon}
    >
      Visualiser dans l’app
    </ButtonLinkNewWindow>
  )
}
