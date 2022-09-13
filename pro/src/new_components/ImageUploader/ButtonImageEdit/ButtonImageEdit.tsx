import React from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { UploaderModeEnum } from '../types'

import { ButtonImageAdd } from './ButtonImageAdd'
import styles from './ButtonImageEdit.module.scss'
import { ModalImageEdit } from './ModalImageEdit'
import { IOnImageUploadArgs } from './ModalImageEdit/ModalImageEdit'
import { IUploadImageValues } from './types'

interface IButtonImageEdit {
  onImageUpload: (values: IOnImageUploadArgs) => Promise<void>
  initialValues?: IUploadImageValues
  mode: UploaderModeEnum
}

const ButtonImageEdit = ({
  mode,
  initialValues = {},
  onImageUpload,
}: IButtonImageEdit): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()
  const { imageUrl, originalImageUrl } = initialValues

  return (
    <>
      {imageUrl || originalImageUrl ? (
        <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
          <Icon
            alt="Modifier l'image"
            className={styles['icon-modify-image']}
            svg="ico-pen-black"
          />
          Modifier
        </Button>
      ) : (
        <ButtonImageAdd onClick={showModal} />
      )}
      {!!visible && (
        <ModalImageEdit
          mode={mode}
          onDismiss={hideModal}
          onImageUpload={onImageUpload}
          initialValues={initialValues}
        />
      )}
    </>
  )
}

export default ButtonImageEdit
