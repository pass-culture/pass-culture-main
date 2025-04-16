import { useCallback } from 'react'

import { useNotification } from 'commons/hooks/useNotification'
import homeShell from 'components/ImageUploader/assets/venue-home-shell.png'
import venueShell from 'components/ImageUploader/assets/venue-shell.png'
import { ImagePreview } from 'components/ImageUploader/components/ImagePreview/ImagePreview'
import { ImagePreviewsWrapper } from 'components/ImageUploader/components/ImagePreview/ImagePreviewsWrapper'

import homeStyle from './HomeScreenPreview.module.scss'
import venueStyle from './VenueScreenPreview.module.scss'

export interface AppPreviewVenueProps {
  imageUrl: string
}

export const AppPreviewVenue = ({
  imageUrl,
}: AppPreviewVenueProps): JSX.Element => {
  const notification = useNotification()

  const showError = useCallback(() => {
    notification.error('Une erreur est survenue. Merci de réessayer plus tard')
  }, [notification])

  return (
    <ImagePreviewsWrapper>
      <ImagePreview title="Page d’accueil">
        <img
          alt=""
          className={homeStyle['image-preview-shell']}
          src={homeShell}
          role="presentation"
        />
        <img
          data-testid="app-preview-venue-img-home"
          alt=""
          className={homeStyle['image-preview-home-preview']}
          onError={showError}
          src={imageUrl}
          role="presentation"
        />
      </ImagePreview>
      <ImagePreview title="Page Lieu">
        <img
          alt=""
          className={venueStyle['image-preview-blur-venue-preview']}
          src={imageUrl}
          role="presentation"
        />
        <img
          alt=""
          className={venueStyle['image-preview-shell']}
          src={venueShell}
          role="presentation"
        />
        <img
          data-testid="app-preview-venue-img"
          alt=""
          className={venueStyle['image-preview-venue-preview']}
          src={imageUrl}
          role="presentation"
        />
      </ImagePreview>
    </ImagePreviewsWrapper>
  )
}
