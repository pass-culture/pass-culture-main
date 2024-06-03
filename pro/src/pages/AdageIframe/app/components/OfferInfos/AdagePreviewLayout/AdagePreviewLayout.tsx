import { useEffect, useState } from 'react'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetVenueResponseModel,
  OfferAddressType,
} from 'apiClient/v1'
import { isCollectiveOffer } from 'core/OfferEducational/types'
import logoPassCultureIcon from 'icons/logo-pass-culture.svg'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { AdageOffer } from '../AdageOffer/AdageOffer'

import styles from './AdagePreviewLayout.module.scss'
import adageBurger from './assets/adage-burger.svg'
import adageLogo from './assets/adage-logo.png'

type AdagePreviewLayoutProps = {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

export const AdagePreviewLayout = ({ offer }: AdagePreviewLayoutProps) => {
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
  }, [offer.id, offer.venue.id])

  if (loadingVenue) {
    return <Spinner />
  }

  if (!venue) {
    return
  }

  const isBookable = isCollectiveOffer(offer) && offer.collectiveStock

  //The venue and offerVenue from the created offer in pro must be modified to match the model of a venue in the adage iframe
  let offerForAdage:
    | CollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel = {
    ...offer,
    isExpired: false,
    isSoldOut: false,
    contactEmail: offer.contactEmail,
    venue: {
      ...offer.venue,
      coordinates: { latitude: venue.latitude, longitude: venue.longitude },
      publicName: venue.publicName,
      postalCode: venue.postalCode,
      city: venue.city,
      address: venue.street,
      departmentCode: venue.departementCode,
    },
  }

  if (isBookable) {
    offerForAdage = {
      ...offerForAdage,
      teacher: offer.teacher,
      educationalInstitution: {
        city: offer.institution?.city ?? '',
        institutionType: offer.institution?.institutionType,
        name: offer.institution?.name ?? '',
        postalCode: offer.institution?.postalCode ?? '',
        id: offer.institution?.id ?? 0,
      },
      stock: {
        ...offer.collectiveStock,
        //  The price is mutliplied by 100 in the back when the offer is sent
        //  through the passculture ADAGE api.
        //  Thus we need to send a x100 prixe in the fake ADAGE component
        price: Number(offer.collectiveStock?.price) * 100,
        id: Number(offer.collectiveStock?.id),
        isBookable: offer.isBookable,
      },
    }
  }

  if (offerForAdage.offerVenue.addressType === OfferAddressType.OFFERER_VENUE) {
    offerForAdage.offerVenue = {
      ...offer.offerVenue,
      name: venue.name,
      publicName: venue.publicName,
      postalCode: venue.postalCode,
      city: venue.city,
      address: venue.street,
    }
  }

  return (
    <div className={styles['fake-adage-page']}>
      <div className={styles['fake-adage-page-header']}>
        <div className={styles['fake-adage-page-header-logo']}>
          <img src={adageLogo} alt="Logo de la plateforme ADAGE" />
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
