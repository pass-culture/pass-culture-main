import React, { FunctionComponent, useCallback, useRef } from 'react'
import AvatarEditor, { CroppedRect } from 'react-avatar-editor'

import { ReactComponent as CloseIcon } from 'icons/ico-clear.svg'
import { CreditInput } from 'new_components/CreditInput/CreditInput'
import ImageEditor from 'new_components/ImageEditor/ImageEditor'
import { Button, Divider } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './VenueImageEdit.module.scss'

const CANVAS_HEIGHT = 244
const CANVAS_WIDTH = (CANVAS_HEIGHT * 3) / 2
const CROP_BORDER_HEIGHT = 40
const CROP_BORDER_WIDTH = 100
const CROP_BORDER_COLOR = '#fff'

type Props = {
  image: string | File
  credit: string
  onSetCredit: (credit: string) => void
  children?: never
  closeModal: () => void
  onEditedImageSave: (dataUrl: string, croppedRect: CroppedRect) => void
}

export const VenueImageEdit: FunctionComponent<Props> = ({
  closeModal,
  image,
  credit,
  onSetCredit,
  onEditedImageSave,
}) => {
  const editorRef = useRef<AvatarEditor>(null)

  const handleNext = useCallback(() => {
    if (editorRef.current) {
      const canvas = editorRef.current.getImage()
      const croppingRect = editorRef.current.getCroppingRect()
      onEditedImageSave(canvas.toDataURL(), croppingRect)
    }
  }, [onEditedImageSave])

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
          ref={editorRef}
        />
        <CreditInput
          credit={credit}
          extraClassName={style['venue-image-edit-credit']}
          updateCredit={onSetCredit}
        />
      </form>
      <Divider />
      <footer className={style['venue-image-edit-footer']}>
        <Button
          Icon={CloseIcon}
          onClick={closeModal}
          variant={ButtonVariant.TERNARY}
        >
          Annuler
        </Button>
        <Button onClick={handleNext}>Suivant</Button>
      </footer>
    </section>
  )
}
