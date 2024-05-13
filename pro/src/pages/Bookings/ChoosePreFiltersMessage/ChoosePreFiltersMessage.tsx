import cn from 'classnames'
import React from 'react'

import strokeBookingHold from 'icons/stroke-booking-hold.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ChoosePreFiltersMessage.module.scss'

const UNBREAKABLE_SPACE = '\u00A0'

export const ChoosePreFiltersMessage = () => (
  <div className={cn(styles['no-data'])}>
    <SvgIcon
      className={styles['no-data-icon']}
      src={strokeBookingHold}
      alt=""
      viewBox="0 0 200 156"
    />
    <p>
      {`Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur «${UNBREAKABLE_SPACE}Afficher${UNBREAKABLE_SPACE}»`}
    </p>
  </div>
)
