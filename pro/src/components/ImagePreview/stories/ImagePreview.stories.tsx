import type { Story } from '@storybook/react'
import React from 'react'

import { ImagePreview } from '../ImagePreview'
import { ImagePreviewsWrapper } from '../ImagePreviewsWrapper'

import style from './HomeScreenShell.module.scss'
import offerHomeShell from './offer-home-shell.png'
import offerPreview from './offer-preview.jpg'
import offerShell from './offer-shell.png'

export default {
  title: 'components/ImagePreview',
  component: ImagePreview,
}

interface Props {
  title: string
}

const Template: Story<Props> = props => (
  <ImagePreviewsWrapper>
    <ImagePreview {...props}>
      <img
        alt=""
        className={style['home-screen-shell']}
        src={offerHomeShell.src}
      />
      <img
        alt=""
        className={style['preview-on-home-screen']}
        src={offerPreview.src}
      />
    </ImagePreview>
    <ImagePreview title="Détails de l’offre">
      <img
        alt=""
        className={style['blurred-preview-on-offer-screen']}
        src={offerPreview.src}
      />
      <img
        alt=""
        className={style['offer-screen-shell']}
        src={offerShell.src}
      />
      <img
        alt=""
        className={style['preview-on-offer-screen']}
        src={offerPreview.src}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)

export const Default = Template.bind({})
Default.args = {
  title: "Page d'accueil",
}
