import React, { useState } from 'react'

import fullShowIcon from 'icons/full-show.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { UploaderModeEnum } from '../types'

import { ModalAppPreview } from './ModalAppPreview'

export interface ButtonAppPreviewProps {
  mode: UploaderModeEnum
  imageUrl: string
}

export const ButtonAppPreview = ({
  imageUrl,
  mode,
}: ButtonAppPreviewProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      <Button
        onClick={() => setIsModalOpen(true)}
        variant={ButtonVariant.TERNARY}
        icon={fullShowIcon}
      >
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
