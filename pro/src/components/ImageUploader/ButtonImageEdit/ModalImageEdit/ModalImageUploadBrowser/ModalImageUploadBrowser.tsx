import React from 'react'

import { ImageUploadBrowserForm } from 'components/ImageUploadBrowserForm'
import { ImageUploadBrowserFormValues } from 'components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { PreferredOrientation } from 'components/PreferredOrientation/PreferredOrientation'

import style from './ModalImageUploadBrowser.module.scss'

interface ModalImageUploadBrowserProps {
  onImageClientUpload: (values: ImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
}

const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
}: ModalImageUploadBrowserProps) => {
  const orientation = {
    [UploaderModeEnum.OFFER]: 'portrait',
    [UploaderModeEnum.OFFER_COLLECTIVE]: 'portrait',
    [UploaderModeEnum.VENUE]: 'landscape',
  }[mode]

  return (
    <section className={style['modal-upload-browser']}>
      <header>
        <h1 className={style['header']}>Ajouter une image</h1>
      </header>

      <PreferredOrientation
        orientation={orientation as 'portrait' | 'landscape'}
      />

      <ImageUploadBrowserForm onSubmit={onImageClientUpload} mode={mode} />
    </section>
  )
}

export default ModalImageUploadBrowser
