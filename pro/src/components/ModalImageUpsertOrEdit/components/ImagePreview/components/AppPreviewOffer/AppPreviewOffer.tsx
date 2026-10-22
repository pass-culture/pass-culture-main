import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import homeShell from '../../assets/offer-home-shell.png'
import offerShell from '../../assets/offer-shell.svg'
import { ImagePreview } from '../../ImagePreview'
import { ImagePreviewsWrapper } from '../../ImagePreviewsWrapper'
import homeStyle from './HomeScreenPreview.module.scss'
import offerStyle from './OfferScreenPreview.module.scss'

interface AppPreviewOfferProps {
  imageUrl: string
}

export const AppPreviewOffer = ({
  imageUrl,
}: AppPreviewOfferProps): JSX.Element => (
  <ImagePreviewsWrapper>
    <ImagePreview title="Page d’accueil">
      <img
        alt=""
        aria-hidden
        className={homeStyle['image-preview-shell']}
        src={homeShell}
      />
      <img
        data-testid="app-preview-offer-img-home"
        alt=""
        aria-hidden
        className={homeStyle['image-preview-home-preview']}
        src={imageUrl}
      />
    </ImagePreview>
    <ImagePreview title="Détails de l’offre">
      <img
        alt=""
        aria-hidden
        className={offerStyle['image-preview-blur-offer-preview']}
        src={imageUrl}
      />
      <SvgIcon
        src={offerShell}
        alt=""
        aria-hidden
        className={offerStyle['image-preview-shell']}
        viewBox="0 0 92 166"
      />
      <img
        data-testid="app-preview-offer-img"
        alt=""
        aria-hidden
        className={offerStyle['image-preview-offer-preview']}
        src={imageUrl}
      />
    </ImagePreview>
  </ImagePreviewsWrapper>
)
