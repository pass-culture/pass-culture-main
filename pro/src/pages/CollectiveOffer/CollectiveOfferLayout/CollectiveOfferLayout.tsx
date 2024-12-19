import { title } from 'process'

import cn from 'classnames'
import React, { useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { HelpLink } from 'components/HelpLink/HelpLink'
import { CollectiveOfferNavigation } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferNavigation/CollectiveOfferNavigation'
import { getActiveStep } from 'pages/CollectiveOfferRoutes/utils/getActiveStep'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { CollectiveEditingOfferNavigation } from './CollectiveEditingOfferNavigation/CollectiveEditingOfferNavigation'
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
}

export const CollectiveOfferLayout = ({
  children,
  subTitle,
  isFromTemplate = false,
  isCreation = false,
  isTemplate = false,
  requestId = null,
  offer,
}: CollectiveOfferLayoutProps): JSX.Element => {
  const location = useLocation()
  const isSummaryPage = location.pathname.includes('recapitulatif')
  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()
  let title = isCreation
    ? isFromTemplate
      ? 'Créer une offre pour un établissement scolaire'
      : 'Créer une nouvelle offre collective'
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
  console.log(subTitle)
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
          {title}{' '}
          <span className={styles['eac-layout-sub-heading']}>{subTitle}</span>
        </h1>
      </div>

      {navigationProps.isCreatingOffer ? (
        <CollectiveOfferNavigation
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
        <CollectiveEditingOfferNavigation
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
