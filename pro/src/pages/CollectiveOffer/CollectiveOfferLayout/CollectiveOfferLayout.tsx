import type React from 'react'
import { useLocation, useParams } from 'react-router'

import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1/new'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { Tag } from '@/design-system/Tag/Tag'
import { CollectiveCreationOfferNavigation } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import { getActiveStep } from '@/pages/CollectiveOfferRoutes/utils/getActiveStep'

import { CollectiveEditionOfferNavigation } from './CollectiveEditionOfferNavigation/CollectiveEditionOfferNavigation'
import styles from './CollectiveOfferLayout.module.scss'

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
  const title = isCreation
    ? isTemplate
      ? 'Créer une offre vitrine'
      : 'Créer une offre réservable'
    : isSummaryPage
      ? 'Récapitulatif'
      : 'Modifier l’offre'

  const navigationProps = {
    activeStep: getActiveStep(location.pathname),
    offerId: offerIdFromParams?.includes('T-')
      ? Number(offerIdFromParams.split('T-')[1])
      : Number(offerIdFromParams),
    isCreatingOffer: isCreation,
  }

  return (
    <BasicLayout
      mainHeading={
        <div className={styles['eac-layout-heading-wrapper']}>
          {isTemplate && <Tag label="Offre vitrine" />}
          {title}
        </div>
      }
      mainSubHeading={subTitle}
      isStickyActionBarInChild
    >
      {/* TODO (igabriele, 2026-04-27): Isn't that the role of routing permissions to guarantee this prop is true? */}
      {selectedPartnerVenue.allowedOnAdage && (
        <>
          {navigationProps.isCreatingOffer && (
            <CollectiveCreationOfferNavigation
              activeStep={navigationProps.activeStep}
              className={styles['eac-layout-navigation']}
              offerId={navigationProps.offerId}
              isTemplate={isTemplate}
              requestId={requestId}
              offer={offer}
            />
          )}
          {!navigationProps.isCreatingOffer && (
            <CollectiveEditionOfferNavigation
              isTemplate={isTemplate}
              offer={offer}
              offerId={navigationProps.offerId}
              activeStep={navigationProps.activeStep}
            />
          )}
        </>
      )}

      {children}
    </BasicLayout>
  )
}
