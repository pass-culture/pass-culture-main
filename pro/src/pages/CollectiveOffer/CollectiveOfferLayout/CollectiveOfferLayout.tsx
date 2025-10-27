import cn from 'classnames'
import type React from 'react'
import { useLocation, useParams } from 'react-router'

import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useIsAllowedOnAdage } from '@/commons/hooks/useIsAllowedOnAdage'
import { HelpLink } from '@/components/HelpLink/HelpLink'
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
  const isSummaryPage = location.pathname.includes('recapitulatif')

  const allowedOnAdage = useIsAllowedOnAdage()

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
      {!allowedOnAdage ? null : navigationProps.isCreatingOffer ? (
        <CollectiveCreationOfferNavigation
          activeStep={navigationProps.activeStep}
          className={cn(styles['eac-layout-navigation'], {
            [styles['stepper-navigation']]: navigationProps.isCreatingOffer,
          })}
          offerId={navigationProps.offerId}
          isTemplate={isTemplate}
          requestId={requestId}
          offer={offer}
        />
      ) : (
        <CollectiveEditionOfferNavigation
          isTemplate={isTemplate}
          offer={offer}
          offerId={navigationProps.offerId}
          activeStep={navigationProps.activeStep}
        />
      )}
      {children}
      <HelpLink />
    </BasicLayout>
  )
}
