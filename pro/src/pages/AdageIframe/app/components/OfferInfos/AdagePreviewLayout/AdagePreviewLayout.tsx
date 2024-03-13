import { useEffect, useState } from 'react'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { api } from 'apiClient/api'
import {
  GetCollectiveOfferTemplateResponseModel,
  GetVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import Spinner from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import AdageOffer from '../AdageOffer/AdageOffer'

import styles from './AdagePreviewLayout.module.scss'
import adageBurger from './assets/adage-burger.svg'
import adageLogo from './assets/adage-logo.png'

type AdagePreviewLayoutProps = {
  offer: GetCollectiveOfferTemplateResponseModel
}

export default function AdagePreviewLayout({ offer }: AdagePreviewLayoutProps) {
  const [venue, setVenue] = useState<GetVenueResponseModel | null>(null)
  const [loadingVenue, setLoadingVenue] = useState(false)
  useState<GetVenueResponseModel | null>(null)

  useEffect(() => {
    async function getOfferVenue() {
      setLoadingVenue(true)
      const venue = await api.getVenue(offer.venue.id)
      setLoadingVenue(false)
      setVenue(venue)
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    getOfferVenue()
  }, [offer.id, offer.venue?.id])

  if (loadingVenue) {
    return <Spinner />
  }

  if (!venue) {
    return
  }

  //The venue and offerVenue from the created offer in pro must be modified to match the model of a venue in the adage iframe
  const offerForAdage: CollectiveOfferTemplateResponseModel = {
    ...offer,
    isExpired: false,
    isSoldOut: false,
    venue: {
      ...offer.venue,
      coordinates: { latitude: venue.latitude, longitude: venue.longitude },
      publicName: venue.publicName,
      postalCode: venue.postalCode,
      city: venue.city,
      address: venue.address,
    },
  }

  if (offerForAdage.offerVenue.addressType === OfferAddressType.OFFERER_VENUE) {
    offerForAdage.offerVenue = {
      ...offer.offerVenue,
      name: venue.name,
      publicName: venue.publicName,
      postalCode: venue.postalCode,
      city: venue.city,
      address: venue.address,
    }
  }

  return (
    <div className={styles['fake-adage-page']}>
      <div className={styles['fake-adage-page-header']}>
        <div className={styles['fake-adage-page-header-logo']}>
          <img src={adageLogo} alt="Logo de la plateforme Adage" />
        </div>
        <img
          src={adageBurger}
          alt=""
          className={styles['fake-adage-page-header-burger']}
          aria-hidden="true"
        />
      </div>
      <div className={styles['fake-adage-page-content']}>
        <div className={styles['fake-adage-page-pass']}>
          <div className={styles['fake-adage-page-pass-header']}>
            <SvgIcon
              src={logoPassCultureIcon}
              alt="Logo du pass Culture"
              width="98"
              viewBox="0 0 71 24"
            />
          </div>
          <div className={styles['fake-adage-page-pass-content']}>
            <AdageOffer offer={offerForAdage} isPreview />
          </div>
        </div>
      </div>
    </div>
  )
}
