import cn from 'classnames'
import { useState } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { UploaderModeEnum } from '../types'

import style from './ButtonImageEdit.module.scss'
import { ModalImageEdit } from './ModalImageEdit'
import { OnImageUploadArgs } from './ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './types'

export type ButtonImageEditProps = {
  onImageUpload: (values: OnImageUploadArgs) => void
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onClickButtonImage?: () => void
}

const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
  onClickButtonImage,
}: ButtonImageEditProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { imageUrl, originalImageUrl } = initialValues

  const onClickButtonImageAdd = () => {
    onClickButtonImage && onClickButtonImage()
    setIsModalOpen(true)
  }

  return (
    <>
      {imageUrl || originalImageUrl ? (
        <Button
          onClick={onClickButtonImageAdd}
          variant={ButtonVariant.TERNARY}
          alt="Modifier l’image"
          icon={fullEditIcon}
        >
          Modifier
        </Button>
      ) : (
        <button
          className={cn(style['button-image-add'], {
            [style['add-image-venue']]: mode === UploaderModeEnum.VENUE,
            [style['add-image-offer']]:
              mode === UploaderModeEnum.OFFER ||
              mode === UploaderModeEnum.OFFER_COLLECTIVE,
          })}
          onClick={onClickButtonImageAdd}
          type="button"
        >
          <SvgIcon src={strokeMoreIcon} alt="" className={style['icon']} />
          <span className={style['label']}>Ajouter une image</span>
        </button>
      )}

      {isModalOpen && (
        <ModalImageEdit
          mode={mode}
          onDismiss={() => setIsModalOpen(false)}
          onImageUpload={onImageUpload}
          initialValues={initialValues}
        />
      )}
    </>
  )
}

export default ButtonImageEdit
