import React, { useState } from 'react'

import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'

import { UploaderModeEnum } from '../types'

import styles from './ButtonAppPreview.module.scss'
import { ModalAppPreview } from './ModalAppPreview'

export interface ButtonAppPreviewProps {
  mode: UploaderModeEnum
  imageUrl: string
}

const ButtonAppPreview = ({
  imageUrl,
  mode,
}: ButtonAppPreviewProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      <Button
        onClick={() => setIsModalOpen(true)}
        variant={ButtonVariant.TERNARY}
      >
        <Icon
          className={styles['image-venue-uploader-section-icon']}
          svg="ico-eye-open-filled-black"
        />
        Prévisualiser
      </Button>

      {isModalOpen && imageUrl && (
        <ModalAppPreview
          mode={mode}
          imageUrl={imageUrl}
          hideModal={() => setIsModalOpen(false)}
        />
      )}
    </>
  )
}

export default ButtonAppPreview
