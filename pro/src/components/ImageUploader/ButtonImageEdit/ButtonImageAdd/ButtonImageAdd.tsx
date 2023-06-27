import cn from 'classnames'
import React from 'react'

import { UploaderModeEnum } from 'components/ImageUploader/types'

import PlusIcon from './assets/plus-icon.svg'
import style from './ButtonImageAdd.module.scss'

export interface IButtonImageAddProps {
  onClick: () => void
  mode: UploaderModeEnum
}

const ButtonImageAdd = ({
  onClick,
  mode,
}: IButtonImageAddProps): JSX.Element => (
  <button
    className={cn(style['button-image-add'], {
      [style['add-image-venue']]: mode === UploaderModeEnum.VENUE,
      [style['add-image-offer']]:
        mode === UploaderModeEnum.OFFER ||
        mode === UploaderModeEnum.OFFER_COLLECTIVE,
    })}
    onClick={onClick}
    type="button"
  >
    <PlusIcon className={style['icon']} />
    <span className={style['label']}>
      Ajouter <br /> une image
    </span>
  </button>
)

export default ButtonImageAdd
