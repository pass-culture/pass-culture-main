import React from 'react'

import { ReactComponent as PlusIcon } from './assets/plus-icon.svg'
import style from './ButtonImageAdd.module.scss'

export interface IButtonImageAddProps {
  onClick: () => void
}

const ButtonImageAdd = ({ onClick }: IButtonImageAddProps): JSX.Element => (
  <button className={style['button-image-add']} onClick={onClick} type="button">
    <PlusIcon className={style['icon']} />
    <span className={style['label']}>Ajouter une image</span>
  </button>
)

export default ButtonImageAdd
