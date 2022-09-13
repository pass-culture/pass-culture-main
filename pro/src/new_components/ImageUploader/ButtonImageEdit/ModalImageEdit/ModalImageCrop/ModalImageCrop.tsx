import React, { useCallback, useRef } from 'react'
import AvatarEditor, { CroppedRect, Position } from 'react-avatar-editor'

import useNotification from 'components/hooks/useNotification'
import { ReactComponent as DownloadIcon } from 'icons/ico-download-filled.svg'
import { CreditInput } from 'new_components/CreditInput/CreditInput'
import ImageEditor, {
  IImageEditorConfig,
} from 'new_components/ImageEditor/ImageEditor'
import { coordonateToPosition } from 'new_components/ImageEditor/utils'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'
import { Button, Divider } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './ModalImageCrop.module.scss'

interface IModalImageCropProps {
  image: string | File
  credit: string
  onSetCredit: (credit: string) => void
  children?: never
  onReplaceImage: () => void
  initialPosition?: Position
  initialScale?: number
  saveInitialScale: (scale: number) => void
  saveInitialPosition: (position: Position) => void
  onEditedImageSave: (dataUrl: string, croppedRect: CroppedRect) => void
  mode: UploaderModeEnum
}

const ModalImageCrop = ({
  onReplaceImage,
  image,
  credit,
  onSetCredit,
  onEditedImageSave,
  saveInitialScale,
  saveInitialPosition,
  initialPosition,
  initialScale,
  mode,
}: IModalImageCropProps): JSX.Element => {
  const editorRef = useRef<AvatarEditor>(null)
  const notification = useNotification()
  const title: string = {
    [UploaderModeEnum.OFFER]: "Image de l'offre",
    [UploaderModeEnum.VENUE]: 'Image du lieu',
  }[mode]
  const canvasHeight: number = {
    [UploaderModeEnum.OFFER]: 384,
    [UploaderModeEnum.VENUE]: 244,
  }[mode]
  const imageEditorConfig: IImageEditorConfig = {
    [UploaderModeEnum.OFFER]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 6) / 9,
      cropBorderColor: '#FFF',
      cropBorderHeight: 50,
      cropBorderWidth: 105,
    },
    [UploaderModeEnum.VENUE]: {
      canvasHeight,
      canvasWidth: (canvasHeight * 3) / 2,
      cropBorderColor: '#FFF',
      cropBorderHeight: 40,
      cropBorderWidth: 100,
    },
  }[mode]

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleNext()
    }
  }

  const handleNext = useCallback(() => {
    try {
      if (editorRef.current) {
        const canvas = editorRef.current.getImage()
        const croppingRect = editorRef.current.getCroppingRect()

        saveInitialPosition({
          x: coordonateToPosition(croppingRect.x, croppingRect.width),
          y: coordonateToPosition(croppingRect.y, croppingRect.height),
        })
        onEditedImageSave(canvas.toDataURL(), croppingRect)
      }
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
    }
  }, [onEditedImageSave, saveInitialPosition, notification])

  return (
    <section className={style['modal-image-crop']}>
      <form action="#" className={style['modal-image-crop-form']}>
        <header>
          <h1 className={style['modal-image-crop-header']}>{title}</h1>
        </header>
        <p className={style['modal-image-crop-right']}>
          En utilisant ce contenu, je certifie que je suis propriétaire ou que
          je dispose des autorisations nécessaires pour l’utilisation de
          celui-ci.
        </p>
        <ImageEditor
          {...imageEditorConfig}
          image={image}
          initialPosition={initialPosition}
          initialScale={initialScale}
          ref={editorRef}
          saveInitialScale={saveInitialScale}
        />
        <CreditInput
          credit={credit}
          extraClassName={style['modal-image-crop-credit']}
          onKeyDown={onKeyDown}
          updateCredit={onSetCredit}
        />
      </form>
      <Divider />
      <footer className={style['modal-image-crop-footer']}>
        <Button
          Icon={DownloadIcon}
          onClick={onReplaceImage}
          variant={ButtonVariant.TERNARY}
        >
          Remplacer l'image
        </Button>
        <Button onClick={handleNext}>Suivant</Button>
      </footer>
    </section>
  )
}

export default ModalImageCrop
