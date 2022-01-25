import React, { FunctionComponent, useCallback } from 'react'

import ImageEditor from 'new_components/ImageEditor/ImageEditor'
import { Button, Divider } from 'ui-kit'

import style from './VenueImageEdit.module.scss'

const CANVAS_HEIGHT = 244
const CANVAS_WIDTH = (CANVAS_HEIGHT * 3) / 2
const CROP_BORDER_HEIGHT = 40
const CROP_BORDER_WIDTH = 100
const CROP_BORDER_COLOR = '#fff'

type Props = {
  image: File
  onSetImage: () => void
  children?: never
}

export const VenueImageEdit: FunctionComponent<Props> = ({
  image,
  onSetImage,
}) => {
  const handleNext = useCallback(() => onSetImage(), [onSetImage])

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
        />
      </form>
      <Divider />
      <footer className={style['venue-image-edit-footer']}>
        <Button onClick={handleNext}>Suivant</Button>
      </footer>
    </section>
  )
}
