import React, { useState } from 'react'

import Advices from 'components/Advices/Advices'
import { ImageUploadBrowserForm } from 'components/ImageUploadBrowserForm'
import { IImageUploadBrowserFormValues } from 'components/ImageUploadBrowserForm/types'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { PreferredOrientation } from 'components/PreferredOrientation/PreferredOrientation'
import { NBSP } from 'core/shared/constants'
import { Divider } from 'ui-kit'

import style from './ModalImageUploadBrowser.module.scss'

interface ModalImageUploadBrowserProps {
  onImageClientUpload: (values: IImageUploadBrowserFormValues) => void
  mode: UploaderModeEnum
}

const ModalImageUploadBrowser = ({
  onImageClientUpload,
  mode,
}: ModalImageUploadBrowserProps) => {
  const [hiddenAdvices, setHiddenAdvices] = useState(true)

  const advicesDescription = {
    [UploaderModeEnum.OFFER]: `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui accompagne votre offre. Les ressources suivantes sont à votre disposition${NBSP}:`,
    [UploaderModeEnum.OFFER_COLLECTIVE]: `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui accompagne votre offre. Les ressources suivantes sont à votre disposition${NBSP}:`,
    [UploaderModeEnum.VENUE]: `Pour maximiser vos chances de réservations, choisissez avec soin l’image qui représente votre lieu. Si vous n’avez pas d'image de votre lieu ou si vous cherchez de bons exemples, les banques d'images suivantes sont à votre disposition${NBSP}:`,
  }[mode]

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
