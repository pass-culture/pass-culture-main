import cn from 'classnames'

import strokeDuoIcon from 'icons/stroke-duo.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DuoCheckbox.module.scss'

export const DuoCheckbox = ({ ...field }) => {
  return (
    <div
      className={cn(styles['duo-checkbox'], {
        [styles['duo-checkbox-selected']]: field.value,
      })}
    >
      <BaseCheckbox
        label="Accepter les réservations duo"
        description="Cette option permet au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur."
        checked={field.value}
        {...field}
      />
      <SvgIcon
        className={styles['duo-checkbox-icon']}
        src={strokeDuoIcon}
        alt="Duo"
        width="40"
      />
    </div>
  )
}
