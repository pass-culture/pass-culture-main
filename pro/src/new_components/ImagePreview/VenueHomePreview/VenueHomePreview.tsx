import React, { FunctionComponent } from 'react'

import { ReactComponent as MobileShell } from 'components/pages/Offers/Offer/Thumbnail/assets/mobile-shell.svg'
import homeShell from 'components/pages/Offers/Offer/Thumbnail/assets/venue-home-shell.png'

import style from './VenueHomePreview.module.scss'

interface Props {
  previewImageURI: string
}

export const VenueHomePreview: FunctionComponent<Props> = ({
  previewImageURI,
}) => (
  <div className="image-preview-previews-wrapper">
    <MobileShell />
    <img alt="" className={style['image-preview-shell']} src={homeShell} />
    <img
      alt=""
      className={style['image-preview-home-preview']}
      src={previewImageURI}
    />
    <div>Page d’accueil</div>
  </div>
)
