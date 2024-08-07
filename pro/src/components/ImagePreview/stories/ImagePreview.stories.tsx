import type { StoryObj } from '@storybook/react'
import React from 'react'

import { ImagePreview, ImagePreviewScreenProps } from '../ImagePreview'
import { ImagePreviewsWrapper } from '../ImagePreviewsWrapper'

import style from './HomeScreenShell.module.scss'
import offerHomeShell from './offer-home-shell.png'
import offerPreview from './offer-preview.jpg'
import offerShell from './offer-shell.png'

export default {
  title: 'components/ImageUploader/ImagePreview',
  component: ImagePreview,
}

const DefaultImagePreview = (props: ImagePreviewScreenProps) => (
  <ImagePreviewsWrapper>
    <ImagePreview {...props}>
      <img alt="" className={style['home-screen-shell']} src={offerHomeShell} />
      <img
        alt=""
        className={style['preview-on-home-screen']}
        src={offerPreview}
      />
    </ImagePreview>
    <ImagePreview title="Détails de l’offre">
      <img
        alt=""
        className={style['blurred-preview-on-offer-screen']}
        src={offerPreview}
      />
      <img alt="" className={style['offer-screen-shell']} src={offerShell} />
      <img
        alt=""
        className={style['preview-on-offer-screen']}
        src={offerPreview}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)

export const Default: StoryObj<typeof ImagePreview> = {
  render: () => <DefaultImagePreview title="Page d'accueil" />,
}
