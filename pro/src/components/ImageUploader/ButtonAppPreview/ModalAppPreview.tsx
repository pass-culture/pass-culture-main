import React from 'react'

import { DialogBox } from 'components/DialogBox/DialogBox'
import { UploaderModeEnum } from 'components/ImageUploader/types'

import { AppPreviewOffer } from '../AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from '../AppPreviewVenue/AppPreviewVenue'

import style from './ModalAppPreview.module.scss'

interface ModalAppPreviewProps {
  hideModal: () => void
  mode: UploaderModeEnum
  imageUrl: string
  children?: never
}

export const ModalAppPreview = ({
  mode,
  hideModal,
  imageUrl,
}: ModalAppPreviewProps): JSX.Element => {
  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  return (
    <DialogBox hasCloseButton labelledBy="add-new-image" onDismiss={hideModal}>
      <div className={style['container']}>
        <header>
          <h1 id="add-new-image" className={style['header']}>
            Ajouter une image
          </h1>
        </header>
        <div className={style['subtitle']}>
          Prévisualisation de votre image dans l’application pass Culture
        </div>
        <AppPreview imageUrl={imageUrl} />
      </div>
    </DialogBox>
  )
}
