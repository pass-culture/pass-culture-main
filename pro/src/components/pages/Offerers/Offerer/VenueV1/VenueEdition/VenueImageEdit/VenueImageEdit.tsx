import React, { useCallback, useRef } from 'react'
import AvatarEditor, { CroppedRect, Position } from 'react-avatar-editor'

import useNotification from 'components/hooks/useNotification'
import { ReactComponent as DownloadIcon } from 'icons/ico-download-filled.svg'
import { CreditInput } from 'new_components/CreditInput/CreditInput'
import ImageEditor from 'new_components/ImageEditor/ImageEditor'
import { coordonateToPosition } from 'new_components/ImageEditor/utils'
import { Button, Divider } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './VenueImageEdit.module.scss'

const CANVAS_HEIGHT = 244
const CANVAS_WIDTH = (CANVAS_HEIGHT * 3) / 2
const CROP_BORDER_HEIGHT = 40
const CROP_BORDER_WIDTH = 100
const CROP_BORDER_COLOR = '#fff'

interface IVenueImageEditProps {
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
}

export const VenueImageEdit = ({
  onReplaceImage,
  image,
  credit,
  onSetCredit,
  onEditedImageSave,
  saveInitialScale,
  saveInitialPosition,
  initialPosition,
  initialScale,
}: IVenueImageEditProps): JSX.Element => {
  const editorRef = useRef<AvatarEditor>(null)
  const notification = useNotification()

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
    <section className={style['venue-image-edit']}>
      <form action="#" className={style['venue-image-edit-form']}>
        <header>
          <h1 className={style['venue-image-edit-header']}>Image du lieu</h1>
        </header>
        <p className={style['venue-image-edit-right']}>
          En utilisant ce contenu, je certifie que je suis propriétaire ou que
          je dispose des autorisations nécessaires pour l’utilisation de
          celui-ci.
        </p>
        <ImageEditor
          canvasHeight={CANVAS_HEIGHT}
          canvasWidth={CANVAS_WIDTH}
          cropBorderColor={CROP_BORDER_COLOR}
          cropBorderHeight={CROP_BORDER_HEIGHT}
          cropBorderWidth={CROP_BORDER_WIDTH}
          image={image}
          initialPosition={initialPosition}
          initialScale={initialScale}
          ref={editorRef}
          saveInitialScale={saveInitialScale}
        />
        <CreditInput
          credit={credit}
          extraClassName={style['venue-image-edit-credit']}
          onKeyDown={onKeyDown}
          updateCredit={onSetCredit}
        />
      </form>
      <Divider />
      <footer className={style['venue-image-edit-footer']}>
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
