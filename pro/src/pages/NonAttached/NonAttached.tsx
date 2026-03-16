import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { Newsletter } from '@/components/Newsletter/Newsletter'

import styles from './NonAttached.module.scss'
import { NonAttachedBanner } from './NonAttachedBanner/NonAttachedBanner'

const NonAttached = () => {
  return (
    <OnboardingLayout
      isEntryScreen
      mainHeading="Bienvenue sur votre espace partenaire"
    >
      <div className={styles['wrapper']}>
        <NonAttachedBanner />
        <br />
        <Newsletter />
      </div>
    </OnboardingLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = NonAttached
