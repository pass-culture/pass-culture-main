import React from 'react'

import { ImagePreview, ImagePreviewsWrapper } from 'new_components/ImagePreview'

import homeShell from '../assets/offer-home-shell.png'
import offerShell from '../assets/offer-shell.png'

import homeStyle from './HomeScreenPreview.module.scss'
import offerStyle from './OfferScreenPreview.module.scss'

export interface IAppPreviewOfferProps {
  imageUrl: string
}

const AppPreviewOffer = ({ imageUrl }: IAppPreviewOfferProps): JSX.Element => (
  <ImagePreviewsWrapper>
    <ImagePreview title="Page d’accueil">
      <img
        alt=""
        className={homeStyle['image-preview-shell']}
        src={homeShell}
      />
      <img
        data-testid="app-preview-offer-img-home"
        alt=""
        className={homeStyle['image-preview-home-preview']}
        src={imageUrl}
      />
    </ImagePreview>
    <ImagePreview title="Détails de l’offre">
      <img
        alt=""
        className={offerStyle['image-preview-blur-offer-preview']}
        src={imageUrl}
      />
      <img
        alt=""
        className={offerStyle['image-preview-shell']}
        src={offerShell}
      />
      <img
        data-testid="app-preview-offer-img"
        alt=""
        className={offerStyle['image-preview-offer-preview']}
        src={imageUrl}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)

export default AppPreviewOffer
