import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from '../assets/mobile-shell.svg'
import offerShell from '../assets/venue-shell.png'
import { ImagePreviewScreenProps } from '../types'

import style from './VenuePreview.module.scss'

export const VenuePreview: FunctionComponent<ImagePreviewScreenProps> = ({
  previewImageURI,
}) => (
  <div className="image-preview-previews-wrapper">
    <MobileShell />
    <img
      alt=""
      className={style['image-preview-blur-venue-preview']}
      src={previewImageURI}
    />
    <img alt="" className={style['image-preview-shell']} src={offerShell} />
    <img
      alt=""
      className={style['image-preview-venue-preview']}
      src={previewImageURI}
    />
    <div>Page Lieu</div>
  </div>
)
