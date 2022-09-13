import React, { useState } from 'react'

import { NBSP } from 'core/shared/constants'
import Advices from 'new_components/Advices/Advices'
import { ImageUploadBrowserForm } from 'new_components/ImageUploadBrowserForm'
import { IImageUploadBrowserFormValues } from 'new_components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'new_components/ImageUploader/types'
import { PreferredOrientation } from 'new_components/PreferredOrientation/PreferredOrientation'
import { Divider } from 'ui-kit'

import style from './ModalImageUploadBrowser.module.scss'

interface IModalImageUploadBrowserProps {
  onImageClientUpload: (values: IImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
}

const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
}: IModalImageUploadBrowserProps) => {
  const [hiddenAdvices, setHiddenAdvices] = useState(true)

  const advicesDescription = {
    [UploaderModeEnum.OFFER]: `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui accompagne votre offre. Les ressources suivantes sont à votre disposition${NBSP}:`,
    [UploaderModeEnum.VENUE]: `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui représente votre lieu. Si vous n'avez pas d'image de votre lieu ou si vous cherchez de bons exemples, les banques d'images suivantes sont à votre disposition${NBSP}:`,
  }[mode]

  const orientation = {
    [UploaderModeEnum.OFFER]: 'portrait',
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
      <Divider className={style['horizontal-rule']} size="large" />
      <Advices
        hidden={hiddenAdvices}
        setHidden={setHiddenAdvices}
        teaserText={advicesDescription}
      />
    </section>
  )
}

export default ModalImageUploadBrowser
