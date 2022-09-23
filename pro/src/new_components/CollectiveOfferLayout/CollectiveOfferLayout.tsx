import React from 'react'

import HelpLink from 'new_components/HelpLink'
import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'new_components/OfferBreadcrumb'
import { Title } from 'ui-kit'

import styles from './CollectiveOfferLayout.module.scss'

interface ICollectiveOfferLayout {
  children: React.ReactNode | React.ReactNode[]
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  offerId?: string
  title: string
}

const CollectiveOfferLayout = ({
  children,
  activeStep,
  isCreatingOffer,
  offerId,
  title,
}: ICollectiveOfferLayout): JSX.Element => {
  return (
    <div className={styles['eac-layout']}>
      <Title className={styles['eac-layout-heading']} level={1}>
        {title}
      </Title>
      <OfferBreadcrumb
        activeStep={activeStep}
        className={styles['eac-layout-breadcrumb']}
        isCreatingOffer={isCreatingOffer}
        isOfferEducational
        offerId={offerId}
      />
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
