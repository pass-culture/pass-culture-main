import cn from 'classnames'
import React from 'react'
import { useSelector } from 'react-redux'
import { useLocation, useParams } from 'react-router'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { Layout } from 'app/App/layout/Layout'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { CollectiveBudgetCallout } from 'components/CollectiveBudgetInformation/CollectiveBudgetCallout'
import { HelpLink } from 'components/HelpLink/HelpLink'
import { Tag } from 'design-system/Tag/Tag'
import { CollectiveCreationOfferNavigation } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferNavigation/CollectiveCreationOfferNavigation'
import { getActiveStep } from 'pages/CollectiveOfferRoutes/utils/getActiveStep'

import { useOfferEducationalFormData } from '../CollectiveOffer/components/OfferEducational/useOfferEducationalFormData'

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
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const offererId = selectedOffererId?.toString()

  const { ...offerEducationalFormData } = useOfferEducationalFormData(
    Number(offererId),
    offer
  )

  const { data: selectedOfferer } = useOfferer(
    offerEducationalFormData.offerer?.id
  )
  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()
  let title = isCreation
    ? isTemplate
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
    <Layout
      layout={'sticky-actions'}
      mainHeading={
        <div className={styles['eac-layout-heading-wrapper']}>
          {isTemplate && (
            <Tag label="Offre vitrine" className={styles['eac-layout-tag']} />
          )}
          {title}
        </div>
      }
      mainSubHeading={subTitle}
    >
      {isCreation && (
        <CollectiveBudgetCallout
          pageName={isTemplate ? 'template-offer-creation' : 'offer-creation'}
        />
      )}
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
    </Layout>
  )
}
