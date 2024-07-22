import React from 'react'

import { AppPreviewOffer } from 'components/ImageUploader/AppPreviewOffer/AppPreviewOffer'
import { AppPreviewVenue } from 'components/ImageUploader/AppPreviewVenue/AppPreviewVenue'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './ModalImageUploadConfirm.module.scss'

interface ModalImageUploadConfirmProps {
  imageUrl: string
  children?: never
  mode: UploaderModeEnum
  isUploading: boolean
  onGoBack: () => void
  onUploadImage: () => void
  idLabelledBy: string
}

export const ModalImageUploadConfirm = ({
  imageUrl,
  isUploading,
  onGoBack,
  onUploadImage,
  mode,
  idLabelledBy,
}: ModalImageUploadConfirmProps): JSX.Element => {
  const AppPreview = {
    [UploaderModeEnum.VENUE]: AppPreviewVenue,
    [UploaderModeEnum.OFFER]: AppPreviewOffer,
    [UploaderModeEnum.OFFER_COLLECTIVE]: AppPreviewOffer,
  }[mode]

  return (
    <div className={style['container']}>
      <header>
        <h1 className={style['header']} id={idLabelledBy}>
          Modifier une image
        </h1>
      </header>
      <div className={style['subtitle']}>
        Prévisualisation de votre image dans l’application pass Culture
      </div>
      <AppPreview imageUrl={imageUrl} />

      <div className={style['actions']}>
        <Button
          className={style['button']}
          onClick={onGoBack}
          title="Retour"
          type="button"
          variant={ButtonVariant.SECONDARY}
        >
          Retour
        </Button>
        <Button
          type="submit"
          className={style['button']}
          disabled={false}
          isLoading={!!isUploading}
          onClick={onUploadImage}
        >
          Enregistrer
        </Button>
      </div>
    </div>
  )
}
