import React, { useState } from 'react'

import { ReactComponent as fullEdit } from 'icons/full-edit.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { UploaderModeEnum } from '../types'

import { ButtonImageAdd } from './ButtonImageAdd'
import { ModalImageEdit } from './ModalImageEdit'
import { IOnImageUploadArgs } from './ModalImageEdit/ModalImageEdit'
import { IUploadImageValues } from './types'

export interface ButtonImageEditProps {
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  initialValues?: IUploadImageValues
  mode: UploaderModeEnum
}

const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
}: ButtonImageEditProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const { imageUrl, originalImageUrl } = initialValues

  return (
    <>
      {imageUrl || originalImageUrl ? (
        <Button
          onClick={() => setIsModalOpen(true)}
          variant={ButtonVariant.TERNARY}
          alt="Modifier l’image"
          Icon={fullEdit}
        >
          Modifier
        </Button>
      ) : (
        <ButtonImageAdd mode={mode} onClick={() => setIsModalOpen(true)} />
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
