import homeShell from 'components/ImageUploader/assets/offer-home-shell.png'
import offerShell from 'components/ImageUploader/assets/offer-shell.png'
import { ImagePreview } from 'components/ImageUploader/components/ImagePreview/ImagePreview'
import { ImagePreviewsWrapper } from 'components/ImageUploader/components/ImagePreview/ImagePreviewsWrapper'

import homeStyle from './HomeScreenPreview.module.scss'
import offerStyle from './OfferScreenPreview.module.scss'

export interface AppPreviewOfferProps {
  imageUrl: string
}

export const AppPreviewOffer = ({
  imageUrl,
}: AppPreviewOfferProps): JSX.Element => (
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
    <ImagePreview title="Détails de l’offre">
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
