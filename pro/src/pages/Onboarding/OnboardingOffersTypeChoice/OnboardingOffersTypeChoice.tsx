import { OnboardingOffersChoice } from 'components/OnboardingOffersChoice/OnboardingOffersChoice'

import { OnboardingLayout } from '../components/OnboardingLayout/OnboardingLayout'

import styles from './OnboardingOffersTypeChoice.module.scss'

export const OnboardingOffersTypeChoice = () => {
  return (
    <OnboardingLayout verticallyCentered stickyActionsAndFooter={false}>
      <div className={styles['onboarding-offer-container']}>
        <div className={styles['onboarding-offer-header']}>
          <h1 className={styles['onboarding-offer-header-title']}>
            Bienvenue sur le pass Culture Pro !
          </h1>
          <h2 className={styles['onboarding-offer-header-subtitle']}>
            À qui souhaitez-vous proposer votre première offre ?{' '}
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
