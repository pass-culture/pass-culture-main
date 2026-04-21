import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { OnboardingOffersChoice } from '@/components/OnboardingOffersChoice/OnboardingOffersChoice'
import { Banner } from '@/design-system/Banner/Banner'

import styles from './OnboardingOffersTypeChoice.module.scss'

export const OnboardingOffersTypeChoice = () => {
  return (
    <OnboardingLayout
      mainHeading="Bienvenue sur pass Culture Pro !"
      verticallyCentered
      isEntryScreen
    >
      <div className={styles['onboarding-offer-container']}>
        <Banner title="Notre équipe vous contactera par email pour vous demander vos justificatifs d’inscription. Pensez à vérifier vos spams." />
        <h2 className={styles['onboarding-offer-header-subtitle']}>
          Où souhaitez-vous diffuser votre première offre ?
        </h2>
        <OnboardingOffersChoice />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OnboardingOffersTypeChoice
