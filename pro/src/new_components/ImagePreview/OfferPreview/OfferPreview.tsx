import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from 'components/pages/Offers/Offer/Thumbnail/assets/mobile-shell.svg'
import offerShell from 'components/pages/Offers/Offer/Thumbnail/assets/offer-shell.png'

import style from './OfferPreview.module.scss'

interface Props {
  previewImageURI: string
}

export const OfferPreview: FunctionComponent<Props> = ({ previewImageURI }) => (
  <div className="image-preview-previews-wrapper">
    <MobileShell />
    <img
      alt=""
      className={style['image-preview-blur-offer-preview']}
      height="435"
      src={previewImageURI}
    />
    <img
      alt=""
      className={style['image-preview-shell']}
      height="280"
      src={offerShell}
    />
    <img
      alt=""
      className={style['image-preview-offer-preview']}
      height="247"
      src={previewImageURI}
    />
    <div>Détails de l’offre</div>
  </div>
)
