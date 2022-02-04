import React, { FunctionComponent } from 'react'

import { ImagePreview } from 'new_components/ImagePreview/ImagePreview'
import { ImagePreviewsWrapper } from 'new_components/ImagePreview/ImagePreviewsWrapper'

import homeShell from '../assets/venue-home-shell.png'
import venueShell from '../assets/venue-shell.png'

import homeStyle from './HomeScreenPreview.module.scss'
import venueStyle from './VenueScreenPreview.module.scss'

interface Props {
  preview: string
}

export const VenuePreviews: FunctionComponent<Props> = ({ preview }) => (
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
        src={preview}
      />{' '}
    </ImagePreview>
    <ImagePreview title="Page Lieu">
      <img
        alt=""
        className={venueStyle['image-preview-blur-venue-preview']}
        src={preview}
      />
      <img
        alt=""
        className={venueStyle['image-preview-shell']}
        src={venueShell}
      />
      <img
        alt=""
        className={venueStyle['image-preview-venue-preview']}
        src={preview}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)
