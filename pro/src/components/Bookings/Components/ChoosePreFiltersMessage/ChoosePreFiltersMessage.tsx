import cn from 'classnames'

import strokeDesk from '@/icons/stroke-desk.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ChoosePreFiltersMessage.module.scss'

const UNBREAKABLE_SPACE = '\u00A0'

export const ChoosePreFiltersMessage = () => (
  <div className={cn(styles['no-data'])}>
    <SvgIcon
      className={styles['no-data-icon']}
      src={strokeDesk}
      alt=""
      viewBox="0 0 48 48"
    />
    <p className={styles['no-data-text']}>
      {`Pour visualiser vos réservations, \nveuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur «${UNBREAKABLE_SPACE}Afficher${UNBREAKABLE_SPACE}»`}
    </p>
  </div>
)
