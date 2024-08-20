import * as Dialog from '@radix-ui/react-dialog'

import { Button } from 'ui-kit/Button/Button'

import topImage from './assets/new-banner-beta.svg'
import styles from './WelcomeToTheNewBetaBanner.module.scss'

export const WelcomeToTheNewBetaBanner = (): JSX.Element => {
  return (
    <div className={styles['banner']}>
      <div className={styles['banner-image']}>
        <img src={topImage} alt="Nouvelle interface" />
      </div>
      <Dialog.Title asChild>
        <h1 id="welcome-on-new-interface" className={styles['banner-title']}>
          Bienvenue sur la nouvelle interface !{' '}
          <span aria-hidden={true}>🎉</span>
        </h1>
      </Dialog.Title>

      <p className={styles['banner-description']}>
        Nous travaillons depuis quelques mois sur cette nouvelle version, pour
        vous proposer un outil plus pratique et plus agréable.
      </p>
      <p className={styles['banner-description']}>
        Nous continuons encore à l’améliorer : vous pouvez nous donner votre
        avis à n’importe quel moment depuis la bannière prévue à cet effet.
      </p>
      <div className={styles['banner-button']}>
        <Dialog.Close asChild>
          <Button>Découvrir</Button>
        </Dialog.Close>
      </div>
    </div>
  )
}
