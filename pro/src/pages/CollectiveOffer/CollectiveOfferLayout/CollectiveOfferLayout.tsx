import cn from 'classnames'
import React from 'react'
import { useLocation, useParams } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  GetEducationalOffererResponseModel,
} from 'apiClient/v1'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { CollectiveBudgetCallout } from 'components/CollectiveBudgetInformation/CollectiveBudgetCallout'
import { HelpLink } from 'components/HelpLink/HelpLink'
import { CollectiveCreationOfferNavigation } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import { getActiveStep } from 'pages/CollectiveOfferRoutes/utils/getActiveStep'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { CollectiveEditionOfferNavigation } from './CollectiveEditionOfferNavigation/CollectiveEditionOfferNavigation'
import styles from './CollectiveOfferLayout.module.scss'

export interface CollectiveOfferLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  subTitle?: string
  isCreation?: boolean
  isTemplate?: boolean
  isFromTemplate?: boolean
  requestId?: string | null
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  userOfferer?: GetEducationalOffererResponseModel | null
}

export const CollectiveOfferLayout = ({
  children,
  subTitle,
  isFromTemplate = false,
  isCreation = false,
  isTemplate = false,
  requestId = null,
  offer,
  userOfferer,
}: CollectiveOfferLayoutProps): JSX.Element => {
  const location = useLocation()
  const isSummaryPage = location.pathname.includes('recapitulatif')

  const { data: selectedOfferer } = useOfferer(userOfferer?.id)
  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()
  let title = isCreation
    ? isFromTemplate
      ? 'Créer une offre vitrine'
      : 'Créer une offre réservable'
    : isSummaryPage
      ? 'Récapitulatif'
      : 'Éditer une offre collective'

  const navigationProps = {
    activeStep: getActiveStep(location.pathname),
    offerId: offerIdFromParams?.includes('T-')
      ? Number(offerIdFromParams.split('T-')[1])
      : Number(offerIdFromParams),
    isCreatingOffer: isCreation,
  }

  return (
    <div className={styles['eac-layout']}>
      <div className={styles['eac-layout-headings']}>
        {isTemplate && (
          <Tag
            variant={TagVariant.SMALL_OUTLINE}
            className={styles['eac-layout-tag']}
          >
            Offre vitrine
          </Tag>
        )}
        {}
        <h1 className={styles['eac-layout-heading']}>
          {title}
          <span className={styles['eac-layout-sub-heading']}>{subTitle}</span>
        </h1>
        {isCreation && (
          <CollectiveBudgetCallout
            pageName={isTemplate ? 'template-offer-creation' : 'offer-creation'}
          />
        )}
      </div>

      {!selectedOfferer?.allowedOnAdage ? (
        <></>
      ) : navigationProps.isCreatingOffer ? (
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
    </div>
  )
}
