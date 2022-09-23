import React from 'react'

import HelpLink from 'new_components/HelpLink'
import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'new_components/OfferBreadcrumb'
import { Title } from 'ui-kit'

import styles from './CollectiveOfferLayout.module.scss'

interface IBreadcrumbProps {
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  offerId?: string
}
interface ICollectiveOfferLayout {
  children: React.ReactNode | React.ReactNode[]
  breadCrumpProps?: IBreadcrumbProps
  title: string
}

const CollectiveOfferLayout = ({
  children,
  breadCrumpProps,
  title,
}: ICollectiveOfferLayout): JSX.Element => {
  return (
    <div className={styles['eac-layout']}>
      <Title className={styles['eac-layout-heading']} level={1}>
        {title}
      </Title>
      {breadCrumpProps && (
        <OfferBreadcrumb
          activeStep={breadCrumpProps.activeStep}
          className={styles['eac-layout-breadcrumb']}
          isCreatingOffer={breadCrumpProps.isCreatingOffer}
          isOfferEducational
          offerId={breadCrumpProps.offerId}
        />
      )}
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
