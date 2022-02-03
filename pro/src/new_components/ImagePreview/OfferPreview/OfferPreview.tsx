import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from '../assets/mobile-shell.svg'
import offerShell from '../assets/offer-shell.png'
import { ImagePreviewScreenProps } from '../types'

import style from './OfferPreview.module.scss'

export const OfferPreview: FunctionComponent<ImagePreviewScreenProps> = ({
  previewImageURI,
}) => (
  <div className="image-preview-previews-wrapper">
    <MobileShell />
    <img
      alt=""
      className={style['image-preview-blur-offer-preview']}
      src={previewImageURI}
    />
    <img alt="" className={style['image-preview-shell']} src={offerShell} />
    <img
      alt=""
      className={style['image-preview-offer-preview']}
      src={previewImageURI}
    />
    <div>Détails de l’offre</div>
  </div>
)
