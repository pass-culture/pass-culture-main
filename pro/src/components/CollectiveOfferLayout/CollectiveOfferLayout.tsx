import cn from 'classnames'
import React from 'react'
import { useLocation, useParams } from 'react-router-dom'

import CollectiveOfferNavigation from 'components/CollectiveOfferNavigation'
import HelpLink from 'components/HelpLink'
import { getActiveStep } from 'pages/CollectiveOfferRoutes/utils/getActiveStep'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import styles from './CollectiveOfferLayout.module.scss'

export interface CollectiveOfferLayoutProps {
  children: React.ReactNode | React.ReactNode[]
  subTitle?: string
  isCreation?: boolean
  isTemplate?: boolean
  isFromTemplate?: boolean
  haveStock?: boolean
  requestId?: string | null
}

const CollectiveOfferLayout = ({
  children,
  subTitle,
  isFromTemplate = false,
  haveStock = false,
  isCreation = false,
  isTemplate = false,
  requestId = null,
}: CollectiveOfferLayoutProps): JSX.Element => {
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

  const navigationProps = isSummaryPage
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
          {subTitle && (
            <span className={styles['eac-layout-sub-heading']}>{subTitle}</span>
          )}
        </h1>
      </div>

      {
        /* istanbul ignore next: DEBT, TO FIX */
        navigationProps && (
          <CollectiveOfferNavigation
            activeStep={navigationProps.activeStep}
            className={cn(styles['eac-layout-navigation'], {
              [styles['stepper-navigation']]: navigationProps.isCreatingOffer,
            })}
            isCreatingOffer={navigationProps.isCreatingOffer}
            isOfferEducational
            offerId={navigationProps.offerId}
            isTemplate={isTemplate}
            haveStock={haveStock}
            requestId={requestId}
          />
        )
      }
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
