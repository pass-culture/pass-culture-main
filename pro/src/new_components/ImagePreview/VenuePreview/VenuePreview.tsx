import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from 'components/pages/Offers/Offer/Thumbnail/assets/mobile-shell.svg'
import offerShell from 'components/pages/Offers/Offer/Thumbnail/assets/venue-shell.png'

import style from './VenuePreview.module.scss'

interface Props {
  previewImageURI: string
}

export const VenuePreview: FunctionComponent<Props> = ({ previewImageURI }) => (
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
