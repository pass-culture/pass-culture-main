import { OnboardingOffersChoice } from 'components/OnboardingOffersChoice/OnboardingOffersChoice'
import fullWaitIcon from 'icons/full-wait.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

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
        <ButtonLink
          icon={fullWaitIcon}
          to="/my-path"
          variant={ButtonVariant.TERNARY}
        >
          Plus tard
        </ButtonLink>
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OnboardingOffersTypeChoice
