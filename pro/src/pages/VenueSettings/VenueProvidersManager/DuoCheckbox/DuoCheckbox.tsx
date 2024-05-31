import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import strokeDuoIcon from 'icons/stroke-duo.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DuoCheckbox.module.scss'

interface DuoCheckboxProps {
  isChecked: boolean
}

export const DuoCheckbox = ({ isChecked }: DuoCheckboxProps) => {
  const [field, meta] = useField({ name: 'isDuo', type: 'checkbox' })
  return (
    <div
      className={cn(styles['duo-checkbox'], {
        [styles['duo-checkbox-selected']]: isChecked,
      })}
    >
      <BaseCheckbox
        label="Accepter les réservations duo"
        description="Cette option permet au bénéficiaire du pass Culture de venir accompagné. La seconde place sera délivrée au même tarif que la première, quel que soit l’accompagnateur."
        aria-invalid={meta.touched && !!meta.error}
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
