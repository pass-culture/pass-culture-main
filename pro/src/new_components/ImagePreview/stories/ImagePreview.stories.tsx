import { Story } from '@storybook/react'
import React from 'react'

import { ImagePreview } from '../ImagePreview'
import { ImagePreviewsWrapper } from '../ImagePreviewsWrapper'

import homeScreenShell from './home-screen-shell.png'
import style from './HomeScreenShell.module.scss'
import offerPreview from './offer-preview.jpg'
import offerScreenShell from './offer-screen-shell.png'

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
        src={homeScreenShell}
      />
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
      <img
        alt=""
        className={style['offer-screen-shell']}
        src={offerScreenShell}
      />
      <img
        alt=""
        className={style['preview-on-offer-screen']}
        src={offerPreview}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)

export const Default = Template.bind({})
Default.args = {
  title: "Page d'accueil",
}
