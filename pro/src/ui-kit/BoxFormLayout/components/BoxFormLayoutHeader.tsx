import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
} from '@/design-system/Button/types'
import fullEditIcon from '@/icons/full-edit.svg'

import style from '../BoxFormLayout.module.scss'

interface BoxFormLayoutHeader {
  title: string
  subtitle?: string
  onClickModify?: () => void
}

export const Header = ({
  title,
  subtitle,
  onClickModify,
}: BoxFormLayoutHeader): JSX.Element => (
  <div className={style['box-form-layout-header']}>
    <div>
      <h3 className={style['box-form-layout-header-title']}>{title}</h3>
      {subtitle && (
        <h4 className={style['box-form-layout-header-subtitle']}>{subtitle}</h4>
      )}
    </div>

    {onClickModify && (
      <Button
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        size={ButtonSize.SMALL}
        onClick={onClickModify}
        icon={fullEditIcon}
        label="Modifier"
      />
    )}
  </div>
)
