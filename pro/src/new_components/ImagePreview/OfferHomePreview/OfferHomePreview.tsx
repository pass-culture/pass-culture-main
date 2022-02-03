import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from '../assets/mobile-shell.svg'
import homeShell from '../assets/offer-home-shell.png'

import style from './OfferHomePreview.module.scss'

interface Props {
  previewImageURI: string
}

export const OfferHomePreview: FunctionComponent<Props> = ({
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
