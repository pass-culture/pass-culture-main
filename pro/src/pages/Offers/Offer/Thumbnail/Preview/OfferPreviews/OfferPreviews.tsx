import React, { FunctionComponent } from 'react'

import { ImagePreview, ImagePreviewsWrapper } from 'new_components/ImagePreview'

import homeShell from '../assets/offer-home-shell.png'
import offerShell from '../assets/offer-shell.png'

import homeStyle from './HomeScreenPreview.module.scss'
import offerStyle from './OfferScreenPreview.module.scss'

interface Props {
  previewImageURI: string
}

export const OfferPreviews: FunctionComponent<Props> = ({
  previewImageURI,
}) => (
  <ImagePreviewsWrapper>
    <ImagePreview title="Page d’accueil">
      <img
        alt=""
        className={homeStyle['image-preview-shell']}
        src={homeShell}
      />
      <img
        alt=""
        className={homeStyle['image-preview-home-preview']}
        src={previewImageURI}
      />
    </ImagePreview>
    <ImagePreview title="Détails de l’offre">
      <img
        alt=""
        className={offerStyle['image-preview-blur-offer-preview']}
        src={previewImageURI}
      />
      <img
        alt=""
        className={offerStyle['image-preview-shell']}
        src={offerShell}
      />
      <img
        alt=""
        className={offerStyle['image-preview-offer-preview']}
        src={previewImageURI}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)
