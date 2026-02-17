import { Outlet, useLocation } from 'react-router'

import { Header } from '@/app/App/layouts/components/Header/Header'
import { BubbleStepper } from '@/components/BubbleStepper/BubbleStepper'
import { Footer } from '@/components/Footer/Footer'
import { SkipLinks } from '@/components/SkipLinks/SkipLinks'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'

import styles from './WelcomeCarousel.module.scss'

const pagesData: {
  [key: string]: {
    title: string
    subtitle: string
    showBubbleStepper: boolean
    nextStepUrl?: string
    previousStepUrl?: string
  }
} = {
  '/bienvenue': {
    title: 'Bienvenue sur pass Culture Pro',
    subtitle: 'Commençons par identifier votre profil',
    showBubbleStepper: false,
    nextStepUrl: '/bienvenue/publics',
  },
  '/bienvenue/publics': {
    title: 'Deux manières de vous faire connaître',
    subtitle:
      'Les jeunes peuvent découvrir vos offres de deux façons différentes',
    showBubbleStepper: true,
    nextStepUrl: '/bienvenue/offres-jeunes',
    previousStepUrl: '/bienvenue',
  },
  '/bienvenue/offres-jeunes': {
    title: 'Offres pour les jeunes via l’application',
    subtitle: 'Diffusez vos offres gratuites ou payantes auprès des 15-21 ans',
    showBubbleStepper: true,
    nextStepUrl: '/bienvenue/offres-scolaires',
    previousStepUrl: '/bienvenue/publics',
  },
  '/bienvenue/offres-scolaires': {
    title: 'Offres pour les groupes scolaires',
    subtitle: 'Intervenez auprès des classes',
    showBubbleStepper: true,
    nextStepUrl: '/bienvenue/avantages',
    previousStepUrl: '/bienvenue/offres-jeunes',
  },
  '/bienvenue/avantages': {
    title: 'Pourquoi rejoindre le pass Culture ?',
    subtitle: 'Découvrez les avantages pour votre structure',
    showBubbleStepper: true,
    nextStepUrl: '/bienvenue/prochaines-etapes',
    previousStepUrl: '/bienvenue/offres-scolaires',
  },
  '/bienvenue/prochaines-etapes': {
    title: 'Comment fonctionne l’inscription ?',
    subtitle: '3 étapes simples avant d’être visible sur le pass Culture',
    showBubbleStepper: false,
  },
}
const pagesWithStepper = Object.keys(pagesData).filter(
  (x) => pagesData[x].showBubbleStepper
)
export const WelcomeCarousel = (): JSX.Element => {
  const location = useLocation()
  const { title, subtitle, showBubbleStepper, nextStepUrl, previousStepUrl } =
    pagesData[location.pathname]
  return (
    <div className={styles.layout}>
      <SkipLinks />
      <Header disableHomeLink={true} isUnauthenticated={true} />
      <div className={styles['page-layout']}>
        {/* biome-ignore lint/correctness/useUniqueElementIds: Layout is used once per page. There cannot be id duplications. */}
        <div id="content-wrapper" className={styles['content-wrapper']}>
          <div className={styles['content-container']}>
            <main id="content" className={styles['content']}>
              <h1 className={styles.title}>{title}</h1>
              <h2 className={styles.subtitle}>{subtitle}</h2>
              <Outlet />
              <div className={styles[`actionbar-container`]}>
                {previousStepUrl && (
                  <Button
                    as="a"
                    to={previousStepUrl}
                    variant={ButtonVariant.SECONDARY}
                    label="Précédent"
                  />
                )}
                {showBubbleStepper && (
                  <BubbleStepper
                    page={pagesWithStepper.indexOf(location.pathname) + 1}
                    total={pagesWithStepper.length}
                    className={styles['actionbar-container-stepper']}
                  />
                )}
                {nextStepUrl && (
                  <Button
                    as="a"
                    to={nextStepUrl}
                    variant={ButtonVariant.PRIMARY}
                    label={previousStepUrl ? 'Suivant' : 'Valider'}
                  />
                )}
                {!nextStepUrl && (
                  <Button
                    as="a"
                    to="/inscription"
                    variant={ButtonVariant.PRIMARY}
                    label="Démarrer l’inscription"
                  />
                )}
              </div>
            </main>
          </div>
          <Footer layout={'basic'} />
        </div>
      </div>
    </div>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = WelcomeCarousel
