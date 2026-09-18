import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { OnboardingOffersChoice } from '@/components/OnboardingOffersChoice/OnboardingOffersChoice'
import { Banner } from '@/design-system/Banner/Banner'
import { Title } from '@/ui-kit/Title/Title'

import styles from './OnboardingOffersTypeChoice.module.scss'

export const OnboardingOffersTypeChoice = () => {
  return (
    <OnboardingLayout verticallyCentered isEntryScreen>
      <div className={styles['onboarding-offer-container']}>
        <div className={styles['onboarding-offer-title-wrapper']}>
          <Title
            level="1"
            title="Bienvenue sur pass Culture Pro !"
            marginBottom="xxl"
          />
        </div>
        <Banner title="Notre équipe vous contactera par email pour vous demander vos justificatifs d’inscription. Pensez à vérifier vos spams." />
        <Title
          level="2"
          title="Où souhaitez-vous diffuser votre première offre ?"
          marginBottom="l"
          marginTop="xxl"
        />
        <OnboardingOffersChoice />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OnboardingOffersTypeChoice
