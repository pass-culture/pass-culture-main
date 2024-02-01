import { useState } from 'react'
import { useLoaderData } from 'react-router-dom'

import { api } from 'apiClient/api'
import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'
import { ImageUploader, UploadImageValues } from 'components/ImageUploader'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import {
  VenueBannerMetaProps,
  buildInitialValues,
} from 'components/VenueForm/ImageUploaderVenue/ImageUploaderVenue'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullDuplicateIcon from 'icons/full-duplicate.svg'
import fullLinkIcon from 'icons/full-link.svg'
import { postImageToVenue } from 'repository/pcapi/pcapi'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { copyTextToClipboard } from 'ui-kit/CopyLink/CopyLink'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { WEBAPP_URL } from 'utils/config'

import { Card } from '../Card'
import { HomepageLoaderData } from '../Homepage'
import { VenueOfferSteps } from '../VenueOfferSteps/VenueOfferSteps'

import styles from './PartnerPage.module.scss'
import { PartnerPageCollectiveSection } from './PartnerPageCollectiveSection'

export interface PartnerPageProps {
  offerer: GetOffererResponseModel
  venue: GetOffererVenueResponseModel
  setSelectedOfferer: (offerer: GetOffererResponseModel) => void
}

export const PartnerPage = ({
  offerer,
  venue,
  setSelectedOfferer,
}: PartnerPageProps) => {
  const { logEvent } = useAnalytics()
  const notify = useNotification()
  const { venueTypes } = useLoaderData() as HomepageLoaderData
  const venueType = venueTypes.find(
    (venueType) => venueType.id === venue.venueTypeCode
  )
  const initialValues = buildInitialValues(
    venue.bannerUrl,
    // There would be a lot of refactoring to remove this "as"
    // it would ask for a global typing refactor of the image uploads
    // on the backend & frontend to synchronise BannerMetaModel with VenueBannerMetaProps
    (venue.bannerMeta as VenueBannerMetaProps | null | undefined) || undefined
  )
  const [imageValues, setImageValues] =
    useState<UploadImageValues>(initialValues)

  const handleOnImageUpload = async ({
    imageFile,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    try {
      const editedVenue = await postImageToVenue(
        venue.id,
        imageFile,
        credit,
        cropParams?.x,
        cropParams?.y,
        cropParams?.height,
        cropParams?.width
      )
      setImageValues(
        buildInitialValues(editedVenue.bannerUrl, editedVenue.bannerMeta)
      )
      // we update the offerer state to keep venue with its new image
      setSelectedOfferer({
        ...offerer,
        managedVenues: (offerer.managedVenues ?? []).map((iteratedVenue) =>
          iteratedVenue.id === venue.id
            ? {
                ...venue,
                bannerUrl: editedVenue.bannerUrl,
                bannerMeta: editedVenue.bannerMeta,
              }
            : iteratedVenue
        ),
      })

      notify.success('Vos modifications ont bien été prises en compte')
    } catch {
      notify.error(
        'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
      )
    }
  }

  const handleOnImageDelete = async () => {
    try {
      await api.deleteVenueBanner(venue.id)

      setImageValues(buildInitialValues())
    } catch {
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
    }
  }

  const logButtonAddClick = () => {
    logEvent?.(Events.CLICKED_ADD_IMAGE, {
      venueId: venue.id,
      imageType: UploaderModeEnum.VENUE,
      isEdition: true,
    })
  }

  const logVenueLinkClick = () => {
    logEvent?.(Events.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK, {
      venueId: venue.id,
    })
  }

  const copyVenueLink = async () => {
    await copyTextToClipboard(venuePreviewLink)
    notify.success('Lien copié !')
    logEvent?.(Events.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK, {
      venueId: venue.id,
    })
  }

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${venue.id}`

  return (
    <Card>
      <div className={styles['header']}>
        <ImageUploader
          className={styles['image-uploader']}
          onImageUpload={handleOnImageUpload}
          onImageDelete={handleOnImageDelete}
          initialValues={imageValues}
          mode={UploaderModeEnum.VENUE}
          hideActionButtons
          onClickButtonImageAdd={logButtonAddClick}
        />

        <div>
          <div className={styles['venue-type']}>{venueType?.label}</div>
          <div className={styles['venue-name']}>
            {venue.publicName || venue.name}
          </div>
          <address className={styles['venue-address']}>
            {venue.address}, {venue.postalCode} {venue.city}
          </address>

          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            className={styles['venue-button']}
            link={{
              to: `/structures/${offerer.id}/lieux/${venue.id}?modification`,
              'aria-label': `Gérer la page ${venue.name}`,
            }}
          >
            Gérer ma page
          </ButtonLink>
        </div>
      </div>

      <VenueOfferSteps
        className={styles['venue-offer-steps']}
        offerer={offerer}
        venue={venue}
        hasVenue
        isInsidePartnerBlock
      />

      {/* TODO handle not visible case (https://passculture.atlassian.net/browse/PC-26280) */}
      <section className={styles['details']}>
        <div>
          <h4 className={styles['details-title']}>Grand public</h4>
          <Tag variant={TagVariant.LIGHT_GREEN}>Visible</Tag>
        </div>

        <p className={styles['details-description']}>
          Votre page partenaire est visible sur l’application pass Culture.
        </p>

        <ButtonLink
          variant={ButtonVariant.TERNARY}
          icon={fullLinkIcon}
          link={{
            to: venuePreviewLink,
            isExternal: true,
            target: '_blank',
          }}
          svgAlt="Nouvelle fenêtre"
          className={styles['details-link']}
          onClick={logVenueLinkClick}
        >
          Voir ma page dans l’application
        </ButtonLink>

        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullDuplicateIcon}
          className={styles['details-link']}
          onClick={copyVenueLink}
        >
          Copier le lien de la page
        </Button>
      </section>

      <PartnerPageCollectiveSection
        collectiveDmsApplications={venue.collectiveDmsApplications}
        venueId={venue.id}
        hasAdageId={venue.hasAdageId}
      />
    </Card>
  )
}
