import cn from 'classnames'
import React from 'react'

import CollectiveOfferBreadcrumb, {
  CollectiveOfferBreadcrumbStep,
} from 'components/CollectiveOfferBreadcrumb'
import HelpLink from 'components/HelpLink'
import { Tag, Title } from 'ui-kit'

import styles from './CollectiveOfferLayout.module.scss'

interface IBreadcrumbProps {
  activeStep: CollectiveOfferBreadcrumbStep
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

      {breadCrumpProps && (
        <CollectiveOfferBreadcrumb
          activeStep={breadCrumpProps.activeStep}
          className={cn(styles['eac-layout-breadcrumb'], {
            [styles['stepper-breadcrumb']]: breadCrumpProps.isCreatingOffer,
          })}
          isCreatingOffer={breadCrumpProps.isCreatingOffer}
          isOfferEducational
          offerId={breadCrumpProps.offerId}
          isTemplate={isTemplate}
        />
      )}
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
