import { MainHeading } from '@/app/App/layout/Layout'
import { OnboardingOffersChoice } from '@/components/OnboardingOffersChoice/OnboardingOffersChoice'

import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'
import styles from './OnboardingOffersTypeChoice.module.scss'

export const OnboardingOffersTypeChoice = () => {
  return (
    <OnboardingLayout verticallyCentered stickyActionsAndFooter={false}>
      <div className={styles['onboarding-offer-container']}>
        <div className={styles['onboarding-offer-header']}>
          {/* eslint-disable-next-line react/forbid-elements */}
          <MainHeading
            mainHeading="Bienvenue sur le pass Culture Pro !"
            className={styles['onboarding-offer-main-heading-wrapper']}
          />
          <h2 className={styles['onboarding-offer-header-subtitle']}>
            Où souhaitez-vous diffuser votre première offre ?
          </h2>
        </div>
        <OnboardingOffersChoice />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OnboardingOffersTypeChoice
