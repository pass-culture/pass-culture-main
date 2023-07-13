import cn from 'classnames'
import React from 'react'

import strokeDeskIcon from 'icons/stroke-desk.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './ChoosePreFiltersMessage.module.scss'

const UNBREAKABLE_SPACE = '\u00A0'

const ChoosePreFiltersMessage = () => (
  <div className={cn('br-warning', styles['choose-prefilters'])}>
    <SvgIcon src={strokeDeskIcon} alt="" className={styles['icon']} />
    <p>
      {`Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur «${UNBREAKABLE_SPACE}Afficher${UNBREAKABLE_SPACE}»`}
    </p>
  </div>
)

export default ChoosePreFiltersMessage
