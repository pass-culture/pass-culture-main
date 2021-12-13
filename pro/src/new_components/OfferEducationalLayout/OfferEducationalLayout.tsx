import React from 'react'

import HelpLink from 'new_components/HelpLink'
import OfferBreadcrumb, {
  OfferBreadcrumbStep,
} from 'new_components/OfferBreadcrumb'
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
    <>
      <Title className={styles.heading} level={1}>
        {title}
      </Title>
      <OfferBreadcrumb
        activeStep={activeStep}
        className={styles.breadcrumb}
        isCreatingOffer={isCreatingOffer}
        isOfferEducational
        offerId={offerId}
      />
      {children}
      <HelpLink />
    </>
  )
}

export default OfferEducationalLayout
