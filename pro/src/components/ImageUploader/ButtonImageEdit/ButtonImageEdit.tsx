import React, { useState } from 'react'

import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { UploaderModeEnum } from '../types'

import { ButtonImageAdd } from './ButtonImageAdd'
import { ModalImageEdit } from './ModalImageEdit'
import { OnImageUploadArgs } from './ModalImageEdit/ModalImageEdit'
import { UploadImageValues } from './types'

export interface ButtonImageEditProps {
  onImageUpload: (values: OnImageUploadArgs) => Promise<void>
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
        <ButtonImageAdd mode={mode} onClick={onClickButtonImageAdd} />
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
