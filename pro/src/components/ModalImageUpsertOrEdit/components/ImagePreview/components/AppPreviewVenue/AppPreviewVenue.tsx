import homeShell from '../../assets/partner-home-shell.png'
import partnerShell from '../../assets/partner-shell.png'
import { ImagePreview } from '../../ImagePreview'
import { ImagePreviewsWrapper } from '../../ImagePreviewsWrapper'
import homeStyle from './HomeScreenPreview.module.scss'
import offerStyle from './OfferScreenPreview.module.scss'

interface AppPreviewVenueProps {
  imageUrl: string
}

export const AppPreviewVenue = ({
  imageUrl,
}: AppPreviewVenueProps): JSX.Element => (
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
        className={offerStyle['image-preview-shell']}
        src={partnerShell}
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
