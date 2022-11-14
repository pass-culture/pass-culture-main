import React from 'react'

import CollectiveOfferBreadcrumb, {
  CollectiveOfferBreadcrumbStep,
} from 'components/CollectiveOfferBreadcrumb'
import HelpLink from 'components/HelpLink'
import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'components/OfferBreadcrumb'
import useActiveFeature from 'hooks/useActiveFeature'
import { Tag, Title } from 'ui-kit'

import styles from './CollectiveOfferLayout.module.scss'

interface IBreadcrumbProps {
  activeStep: OfferBreadcrumbStep | CollectiveOfferBreadcrumbStep
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
  const isSubtypeChosenAtCreation = useActiveFeature(
    'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION'
  )

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
        breadCrumpProps &&
          (isSubtypeChosenAtCreation ? (
            <CollectiveOfferBreadcrumb
              // @ts-expect-error once the feature flag is removed the only type possible will be correct
              activeStep={breadCrumpProps.activeStep}
              className={styles['eac-layout-breadcrumb']}
              isCreatingOffer={breadCrumpProps.isCreatingOffer}
              isOfferEducational
              offerId={breadCrumpProps.offerId}
              isTemplate={isTemplate}
            />
          ) : (
            <OfferBreadcrumb
              // @ts-expect-error once the feature flag is removed this code disappears
              activeStep={breadCrumpProps.activeStep}
              className={styles['eac-layout-breadcrumb']}
              isCreatingOffer={breadCrumpProps.isCreatingOffer}
              isOfferEducational
              offerId={breadCrumpProps.offerId}
            />
          ))
      }
      {children}
      <HelpLink />
    </div>
  )
}

export default CollectiveOfferLayout
