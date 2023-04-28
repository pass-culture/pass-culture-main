import cn from 'classnames'
import React from 'react'
import { useLocation, useParams } from 'react-router-dom'

import CollectiveOfferBreadcrumb from 'components/CollectiveOfferBreadcrumb'
import HelpLink from 'components/HelpLink'
import { getActiveStep } from 'pages/CollectiveOfferRoutes/utils/getActiveStep'
import { Tag, Title } from 'ui-kit'

import styles from './CollectiveOfferLayout.module.scss'

export interface ICollectiveOfferLayout {
  children: React.ReactNode | React.ReactNode[]
  subTitle?: string
  isCreation?: boolean
  isTemplate?: boolean
  isFromTemplate?: boolean
  haveStock?: boolean
}

const CollectiveOfferLayout = ({
  children,
  subTitle,
  isFromTemplate = false,
  haveStock = false,
  isCreation = false,
  isTemplate = false,
}: ICollectiveOfferLayout): JSX.Element => {
  const location = useLocation()
  const isSummaryPage = location.pathname.includes('recapitulatif')
  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()
  let title = ''
  if (isCreation) {
    if (isFromTemplate) {
      title = 'Créer une offre pour un établissement scolaire'
    } else {
      title = 'Créer une nouvelle offre collective'
    }
  } else {
    if (isSummaryPage) {
      title = 'Récapitulatif'
    } else {
      title = 'Éditer une offre collective'
    }
  }

  const breadCrumpProps = isSummaryPage
    ? undefined
    : {
        activeStep: getActiveStep(location.pathname),
        offerId: Number(offerIdFromParams),
        isCreatingOffer: isCreation,
      }
  return (
    <div className={styles['eac-layout']}>
      <div className={styles['eac-layout-headings']}>
        {isTemplate && (
          <Tag label="Offre vitrine" className={styles['eac-layout-tag']} />
        )}
        {}
        <Title level={1}>{title}</Title>

        {subTitle && (
          <Title level={4} className={styles['eac-layout-sub-heading']}>
            {subTitle}
          </Title>
        )}
      </div>

      {
        /* istanbul ignore next: DEBT, TO FIX */
        breadCrumpProps && (
          <CollectiveOfferBreadcrumb
            activeStep={breadCrumpProps.activeStep}
            className={cn(styles['eac-layout-breadcrumb'], {
              [styles['stepper-breadcrumb']]: breadCrumpProps.isCreatingOffer,
            })}
            isCreatingOffer={breadCrumpProps.isCreatingOffer}
            isOfferEducational
            offerId={breadCrumpProps.offerId}
            isTemplate={isTemplate}
            haveStock={haveStock}
          />
        )
      }
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
