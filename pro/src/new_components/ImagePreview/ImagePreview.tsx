import React, { FunctionComponent } from 'react'

import homeShell from 'components/pages/Offers/Offer/Thumbnail/assets/home-shell.png'
import { ReactComponent as MobileShell } from 'components/pages/Offers/Offer/Thumbnail/assets/mobile-shell.svg'
import offerShell from 'components/pages/Offers/Offer/Thumbnail/assets/offer-shell.png'

interface Props {
  preview: string
}

export const ImagePreview: FunctionComponent<Props> = ({ preview }) => (
  <div className="image-preview-previews">
    <div className="image-preview-previews-wrapper">
      <MobileShell />
      <img
        alt=""
        className="image-preview-shell"
        height="515"
        src={homeShell}
      />
      <img
        alt=""
        className="image-preview-home-preview"
        height="228"
        src={preview}
      />
      <div>Page d’accueil</div>
    </div>
    <div className="image-preview-previews-wrapper">
      <MobileShell />
      <img
        alt=""
        className="image-preview-blur-offer-preview"
        height="435"
        src={preview}
      />
      <img
        alt=""
        className="image-preview-shell right"
        height="280"
        src={offerShell}
      />
      <img
        alt=""
        className="image-preview-offer-preview"
        height="247"
        src={preview}
      />
      <div>Détails de l’offre</div>
    </div>
  </div>
)
