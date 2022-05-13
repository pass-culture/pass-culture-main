import React, { FunctionComponent } from 'react'

import { DisplayInAppLink } from 'new_components/DisplayInAppLink'
import Icon from 'components/layout/Icon'
import { WEBAPP_URL } from 'utils/config'
import cn from 'classnames'
import styles from './DisplayVenueInAppLink.module.scss'

interface Props {
  className?: string
  nonHumanizedId: number
  children?: never
}

export const DisplayVenueInAppLink: FunctionComponent<Props> = ({
  className,
  nonHumanizedId,
}) => {
  const venuePreviewUrl = `${WEBAPP_URL}/lieu/${nonHumanizedId}`

  return (
    <DisplayInAppLink
      className={cn(
        'button-ternary',
        styles['display-venue-link-container'],
        className
      )}
      link={venuePreviewUrl}
    >
      <Icon
        className={styles['display-venue-link-icon']}
        svg="ico-eye-open-filled"
      />
      Visualiser dans l’app
    </DisplayInAppLink>
  )
}
