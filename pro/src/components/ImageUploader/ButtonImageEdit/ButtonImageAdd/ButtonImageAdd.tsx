import cn from 'classnames'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import style from './ButtonImageAdd.module.scss'

interface ButtonImageAddProps {
  onClick: () => void
  mode: UploaderModeEnum
}

const ButtonImageAdd = ({
  onClick,
  mode,
}: ButtonImageAddProps): JSX.Element => (
  <button
    className={cn(style['button-image-add'], {
      [style['add-image-venue']]: mode === UploaderModeEnum.VENUE,
      [style['add-image-offer']]:
        mode === UploaderModeEnum.OFFER ||
        mode === UploaderModeEnum.OFFER_COLLECTIVE,
    })}
    onClick={onClick}
    type="button"
    data-testid="add-image-button"
  >
    <SvgIcon src={strokeMoreIcon} alt="" className={style['icon']} />
    <span className={style['label']}>
      Ajouter <br /> une image
    </span>
  </button>
)

export default ButtonImageAdd
