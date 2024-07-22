import cn from 'classnames'
import { useState } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { UploaderModeEnum } from '../types'

import style from './ButtonImageEdit.module.scss'
import {
  ModalImageEdit,
  OnImageUploadArgs,
} from './ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './types'

export type ButtonImageEditProps = {
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
  initialValues?: UploadImageValues
  mode: UploaderModeEnum
  onClickButtonImage?: () => void
  children?: React.ReactNode
}

export const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
  onImageDelete,
  onClickButtonImage,
  children,
}: ButtonImageEditProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { imageUrl, originalImageUrl } = initialValues

  const onClickButtonImageAdd = () => {
    onClickButtonImage && onClickButtonImage()
    setIsModalOpen(true)
  }

  const handleImageDelete = () => {
    onImageDelete()
    setIsModalOpen(false)
  }

  return (
    <>
      {imageUrl || originalImageUrl ? (
        <Button
          onClick={onClickButtonImageAdd}
          variant={ButtonVariant.TERNARY}
          aria-label="Modifier l’image"
          icon={fullEditIcon}
        >
          {children ?? 'Modifier'}
        </Button>
      ) : (
        <button
          className={cn(style['button-image-add'], {
            [style['add-image-venue'] ?? '']: mode === UploaderModeEnum.VENUE,
            [style['add-image-offer'] ?? '']:
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
          onImageDelete={handleImageDelete}
          initialValues={initialValues}
        />
      )}
    </>
  )
}
