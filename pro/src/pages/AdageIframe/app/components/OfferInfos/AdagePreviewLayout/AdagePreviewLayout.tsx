import useSWR from 'swr'

import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { api } from '@/apiClient/api'
import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { GET_VENUE_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { isCollectiveOffer } from '@/commons/core/OfferEducational/types'
import logoPassCultureIcon from '@/icons/logo-pass-culture.svg'
import { Spinner } from '@/ui-kit/Spinner/Spinner'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

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
  const { data: venue, isLoading } = useSWR(
    [GET_VENUE_QUERY_KEY, offer.venue.id],
    ([, venueIdParam]) => api.getVenue(Number(venueIdParam))
  )

  if (isLoading) {
    return <Spinner />
  }
  if (!venue) {
    return
  }

  const isBookable = isCollectiveOffer(offer) && offer.collectiveStock

  const offerForAdage:
    | CollectiveOfferTemplateResponseModel
    | CollectiveOfferResponseModel = {
    ...offer,
    contactEmail: offer.contactEmail,
    venue: {
      ...offer.venue,
      coordinates: {
        latitude: venue.location?.latitude,
        longitude: venue.location?.longitude,
      },
      publicName: venue.publicName,
      postalCode: venue.location?.postalCode,
      city: venue.location?.city,
      address: venue.location?.street,
      departmentCode: venue.location?.departmentCode,
    },
    isTemplate: !isCollectiveOffer(offer),
    ...(isBookable && {
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
        price: Number(offer.collectiveStock?.price) * 100,
        id: Number(offer.collectiveStock?.id),
      },
    }),
  }

  return (
    <div className={styles['fake-adage-page']}>
      <div className={styles['fake-adage-page-header']}>
        <div className={styles['fake-adage-page-header-logo']}>
          <img src={adageLogo} alt="Plateforme ADAGE" />
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
              alt="pass Culture"
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
