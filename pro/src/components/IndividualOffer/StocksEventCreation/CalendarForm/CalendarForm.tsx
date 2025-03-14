import fullMoreIcon from 'icons/full-more.svg'
import strokeAddCalendarIcon from 'icons/stroke-add-calendar.svg'
import { Button } from 'ui-kit/Button/Button'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CalendarForm.module.scss'

export function CalendarForm() {
  return (
    <div className={styles['container']}>
      <h2 className={styles['title']}>Calendrier</h2>
      <div className={styles['content']}>
        <div className={styles['icon-container']}>
          <SvgIcon className={styles['icon']} src={strokeAddCalendarIcon} />
        </div>
        <Button className={styles['button']} icon={fullMoreIcon}>
          Définir le calendrier
        </Button>
      </div>
    </div>
  )
}
