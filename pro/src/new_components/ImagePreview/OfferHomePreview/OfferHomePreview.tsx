import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from '../assets/mobile-shell.svg'
import homeShell from '../assets/offer-home-shell.png'
import { ImagePreviewScreenProps } from '../types'

import style from './OfferHomePreview.module.scss'

export const OfferHomePreview: FunctionComponent<ImagePreviewScreenProps> = ({
  previewImageURI,
}) => (
  <div className="image-preview-previews-wrapper">
    <MobileShell />
    <img alt="" className={style['image-preview-shell']} src={homeShell} />
    <img
      alt=""
      className={style['image-preview-home-preview']}
      src={previewImageURI}
    />
    <div>Page d’accueil</div>
  </div>
)
