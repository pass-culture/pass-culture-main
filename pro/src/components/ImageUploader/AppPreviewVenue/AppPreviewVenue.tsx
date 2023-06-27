import React, { useCallback } from 'react'

import { ImagePreview, ImagePreviewsWrapper } from 'components/ImagePreview'
import useNotification from 'hooks/useNotification'

import homeShell from '../assets/venue-home-shell.png'
import venueShell from '../assets/venue-shell.png'

import homeStyle from './HomeScreenPreview.module.scss'
import venueStyle from './VenueScreenPreview.module.scss'

export interface AppPreviewVenueProps {
  imageUrl: string
}

const AppPreviewVenue = ({ imageUrl }: AppPreviewVenueProps): JSX.Element => {
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
        />
        <img
          data-testid="app-preview-venue-img-home"
          alt=""
          className={homeStyle['image-preview-home-preview']}
          onError={showError}
          src={imageUrl}
        />
      </ImagePreview>
      <ImagePreview title="Page Lieu">
        <img
          alt=""
          className={venueStyle['image-preview-blur-venue-preview']}
          src={imageUrl}
        />
        <img
          alt=""
          className={venueStyle['image-preview-shell']}
          src={venueShell}
        />
        <img
          data-testid="app-preview-venue-img"
          alt=""
          className={venueStyle['image-preview-venue-preview']}
          src={imageUrl}
        />
      </ImagePreview>
    </ImagePreviewsWrapper>
  )
}

export default AppPreviewVenue
