import React from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { UploaderModeEnum } from '../types'

import styles from './ButtonAppPreview.module.scss'
import { ModalAppPreview } from './ModalAppPreview'

export interface IButtonAppPreviewProps {
  mode: UploaderModeEnum
  imageUrl: string
}

const ButtonAppPreview = ({
  imageUrl,
  mode,
}: IButtonAppPreviewProps): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()
  return (
    <>
      <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
        <Icon
          className={styles['image-venue-uploader-section-icon']}
          svg="ico-eye-open-filled-black"
        />
        Prévisualiser
      </Button>
      {visible && imageUrl && (
        <ModalAppPreview
          mode={mode}
          imageUrl={imageUrl}
          hideModal={hideModal}
        />
      )}
    </>
  )
}

export default ButtonAppPreview
