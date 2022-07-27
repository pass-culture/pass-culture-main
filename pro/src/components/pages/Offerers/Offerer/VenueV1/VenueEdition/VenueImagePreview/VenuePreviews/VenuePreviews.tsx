import React, { useCallback } from 'react'

import useNotification from 'components/hooks/useNotification'
import { ImagePreview, ImagePreviewsWrapper } from 'new_components/ImagePreview'

import homeShell from '../assets/venue-home-shell.png'
import venueShell from '../assets/venue-shell.png'

import homeStyle from './HomeScreenPreview.module.scss'
import venueStyle from './VenueScreenPreview.module.scss'

interface IVenuePreviewsProps {
  preview: string
}

export const VenuePreviews = ({
  preview,
}: IVenuePreviewsProps): JSX.Element => {
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
          alt=""
          className={homeStyle['image-preview-home-preview']}
          onError={showError}
          src={preview}
        />
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
}
