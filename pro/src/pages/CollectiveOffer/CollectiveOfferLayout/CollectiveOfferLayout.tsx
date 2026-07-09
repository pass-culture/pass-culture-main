import type React from 'react'
import { useLocation } from 'react-router'

import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { withVenueHelpers } from '@/commons/utils/withVenueHelpers'
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

type CollectiveOfferNavigationProps = {
  pathname: string
  isCreation: boolean
  offer?: GetCollectiveOfferResponseModel
  requestId: string | null
}

function _renderCollectiveOfferNavigation({
  offer,
  isCreation,
  requestId,
  pathname,
}: CollectiveOfferNavigationProps) {
  const activeStep = getCollectiveOfferActiveStep(pathname)
  if (isCreation) {
    return (
      <CollectiveOfferCreationNavigation
        activeStep={activeStep}
        requestId={requestId}
        offer={offer}
      />
    )
  }
  return (
    <CollectiveOfferEditionNavigation
      activeStep={activeStep}
      offerId={offer?.id}
    />
  )
}

type CollectiveOfferTemplateNavigationProps = {
  pathname: string
  isCreation: boolean
  offer?: GetCollectiveOfferTemplateResponseModel
}

function _renderCollectiveOfferTemplateNavigation({
  offer,
  isCreation,
  pathname,
}: CollectiveOfferTemplateNavigationProps) {
  const activeStep = getCollectiveOfferTemplateActiveStep(pathname)
  if (isCreation) {
    return (
      <CollectiveOfferTemplateCreationNavigation
        activeStep={activeStep}
        offer={offer}
      />
    )
  }
  return <CollectiveOfferTemplateEditionNavigation offer={offer} />
}

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
  const pathname = location.pathname
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isSummaryPage = pathname.includes('recapitulatif')
  const getTitle = () => {
    if (isCreation && isTemplate) return 'Créer une offre vitrine'
    if (isCreation) return 'Créer une offre réservable'
    if (isSummaryPage) return 'Récapitulatif'
    return "Modifier l'offre"
  }

  const isTemplateOffer =
    (!offer && isTemplate) || isCollectiveOfferTemplate(offer)

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

      {!withVenueHelpers(selectedPartnerVenue).isClosed && (
        <>
          {/* TODO (igabriele, 2026-04-27): Isn't that the role of routing permissions to guarantee this prop is true? */}
          {selectedPartnerVenue.allowedOnAdage &&
            (isTemplateOffer
              ? _renderCollectiveOfferTemplateNavigation({
                  isCreation,
                  pathname,
                  offer,
                })
              : _renderCollectiveOfferNavigation({
                  isCreation,
                  pathname,
                  offer,
                  requestId,
                }))}
        </>
      )}

      {children}
    </BasicLayout>
  )
}
