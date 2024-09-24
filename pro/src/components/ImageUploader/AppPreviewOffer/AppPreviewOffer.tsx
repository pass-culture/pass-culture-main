import React from 'react'
import { useTranslation } from 'react-i18next'

import { ImagePreview } from 'components/ImagePreview/ImagePreview'
import { ImagePreviewsWrapper } from 'components/ImagePreview/ImagePreviewsWrapper'

import homeShell from '../assets/offer-home-shell.png'
import offerShell from '../assets/offer-shell.png'

import homeStyle from './HomeScreenPreview.module.scss'
import offerStyle from './OfferScreenPreview.module.scss'

export interface AppPreviewOfferProps {
  imageUrl: string
}

export const AppPreviewOffer = ({
  imageUrl,
}: AppPreviewOfferProps): JSX.Element => {
  const { t } = useTranslation('common')

  return (
    <ImagePreviewsWrapper>
      <ImagePreview title="Page d’accueil">
        <img
          alt=""
          className={homeStyle['image-preview-shell']}
          src={homeShell}
          role="presentation"
        />
        <img
          data-testid="app-preview-offer-img-home"
          alt=""
          className={homeStyle['image-preview-home-preview']}
          src={imageUrl}
          role="presentation"
        />
      </ImagePreview>
      <ImagePreview title={t('offer_details')}>
        <img
          alt=""
          className={offerStyle['image-preview-blur-offer-preview']}
          src={imageUrl}
          role="presentation"
        />
        <img
          alt=""
          className={offerStyle['image-preview-shell']}
          src={offerShell}
          role="presentation"
        />
        <img
          data-testid="app-preview-offer-img"
          alt=""
          className={offerStyle['image-preview-offer-preview']}
          src={imageUrl}
          role="presentation"
        />
      </ImagePreview>
    </ImagePreviewsWrapper>
  )
}
