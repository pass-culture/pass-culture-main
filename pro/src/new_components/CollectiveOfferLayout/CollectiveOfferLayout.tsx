import React from 'react'

import HelpLink from 'new_components/HelpLink'
import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'new_components/OfferBreadcrumb'
import { Tag, Title } from 'ui-kit'

import styles from './CollectiveOfferLayout.module.scss'

interface IBreadcrumbProps {
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  offerId?: string
}
interface ICollectiveOfferLayout {
  children: React.ReactNode | React.ReactNode[]
  breadCrumpProps?: IBreadcrumbProps
  isTemplate?: boolean
  title: string
  subTitle?: string
}

const CollectiveOfferLayout = ({
  children,
  breadCrumpProps,
  isTemplate = false,
  title,
  subTitle,
}: ICollectiveOfferLayout): JSX.Element => {
  return (
    <div className={styles['eac-layout']}>
      <div className={styles['eac-layout-headings']}>
        {isTemplate && (
          <Tag label="Offre vitrine" className={styles['eac-layout-tag']} />
        )}
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
          <OfferBreadcrumb
            activeStep={breadCrumpProps.activeStep}
            className={styles['eac-layout-breadcrumb']}
            isCreatingOffer={breadCrumpProps.isCreatingOffer}
            isOfferEducational
            offerId={breadCrumpProps.offerId}
          />
        )
      }
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
