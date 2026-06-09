import type React from 'react'
import { useLocation, useParams } from 'react-router'

import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1/new'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Tag } from '@/design-system/Tag/Tag'
import {
  getCollectiveOfferActiveStep,
  getCollectiveOfferTemplateActiveStep,
} from '@/pages/CollectiveOffer/CollectiveOfferLayout/utils/getActiveStep'

import styles from './CollectiveOfferLayout.module.scss'
import { CollectiveOfferCreationNavigation } from './CollectiveOfferNavigation/CollectiveOfferCreationNavigation'
import { CollectiveOfferEditionNavigation } from './CollectiveOfferNavigation/CollectiveOfferEditionNavigation'
import { CollectiveOfferTemplateCreationNavigation } from './CollectiveOfferTemplateNavigation/CollectiveOfferTemplateCreationNavigation'
import { CollectiveOfferTemplateEditionNavigation } from './CollectiveOfferTemplateNavigation/CollectiveOfferTemplateEditionNavigation'

export interface CollectiveOfferLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  subTitle?: string
  isCreation?: boolean
  isTemplate?: boolean
  requestId?: string | null
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferLayout = ({
  children,
  subTitle,
  isCreation = false,
  isTemplate = false,
  requestId = null,
  offer,
}: CollectiveOfferLayoutProps): JSX.Element => {
  const location = useLocation()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isSummaryPage = location.pathname.includes('recapitulatif')

  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()

  const getTitle = () => {
    if (isCreation && isTemplate) return 'Créer une offre vitrine'
    if (isCreation) return 'Créer une offre réservable'
    if (isSummaryPage) return 'Récapitulatif'
    return "Modifier l'offre"
  }

  const offerId = offerIdFromParams?.includes('T-')
    ? Number(offerIdFromParams.split('T-')[1])
    : Number(offerIdFromParams)

  const isOfferTemplate = !!offer && isCollectiveOfferTemplate(offer)
  const isCollectiveOffer = !!offer && !isCollectiveOfferTemplate(offer)

  return (
    <BasicLayout isStickyActionBarInChild>
      <MainHeading
        mainHeading={
          <div className={styles['eac-layout-heading-wrapper']}>
            {isTemplate && <Tag label="Offre vitrine" />}
            {getTitle()}
          </div>
        }
        mainSubHeading={subTitle}
      />
      {/* TODO (igabriele, 2026-04-27): Isn't that the role of routing permissions to guarantee this prop is true? */}
      {selectedPartnerVenue.allowedOnAdage && (
        <>
          {!offer &&
            isCreation &&
            (isTemplate ? (
              <CollectiveOfferTemplateCreationNavigation
                activeStep={getCollectiveOfferTemplateActiveStep(
                  location.pathname
                )}
              />
            ) : (
              <CollectiveOfferCreationNavigation
                activeStep={getCollectiveOfferActiveStep(location.pathname)}
                requestId={requestId}
              />
            ))}
          {isCollectiveOffer &&
            (isCreation ? (
              <CollectiveOfferCreationNavigation
                activeStep={getCollectiveOfferActiveStep(location.pathname)}
                offerId={offerId}
                requestId={requestId}
                offer={offer}
              />
            ) : (
              <CollectiveOfferEditionNavigation
                activeStep={getCollectiveOfferActiveStep(location.pathname)}
                offerId={offerId}
              />
            ))}
          {isOfferTemplate &&
            (isCreation ? (
              <CollectiveOfferTemplateCreationNavigation
                activeStep={getCollectiveOfferTemplateActiveStep(
                  location.pathname
                )}
                offerId={offerId}
                offer={offer}
              />
            ) : (
              <CollectiveOfferTemplateEditionNavigation
                offer={offer}
                offerId={offerId}
              />
            ))}
        </>
      )}

      {children}
    </BasicLayout>
  )
}
