import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'new_components/OfferBreadcrumb'

import HelpLink from 'new_components/HelpLink'
import React from 'react'
import { Title } from 'ui-kit'
import styles from './OfferEducationalLayout.module.scss'

interface IOfferEducationalLayout {
  children: React.ReactNode | React.ReactNode[]
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  offerId?: string
  title: string
}

const OfferEducationalLayout = ({
  children,
  activeStep,
  isCreatingOffer,
  offerId,
  title,
}: IOfferEducationalLayout): JSX.Element => {
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

export default OfferEducationalLayout
