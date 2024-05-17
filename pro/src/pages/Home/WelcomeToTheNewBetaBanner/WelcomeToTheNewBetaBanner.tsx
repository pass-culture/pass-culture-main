import React from 'react'

import { DialogBox } from 'components/DialogBox/DialogBox'
import { Button } from 'ui-kit/Button/Button'

import topImage from './assets/new-banner-beta.svg'
import styles from './WelcomeToTheNewBetaBanner.module.scss'

type WelcomeToTheNewBetaBannerProps = {
  setIsNewNavEnabled: (state: boolean) => void
}
export const WelcomeToTheNewBetaBanner = ({
  setIsNewNavEnabled,
}: WelcomeToTheNewBetaBannerProps): JSX.Element => {
  return (
    <DialogBox
      labelledBy=""
      hasCloseButton={true}
      onDismiss={() => setIsNewNavEnabled(false)}
      extraClassNames={styles['banner']}
      closeButtonClassName={styles['banner-close']}
    >
      <div className={styles['banner-image']}>
        <img src={topImage} alt="Nouvelle interface" />
      </div>
      <h2 className={styles['banner-title']}>
        Bienvenue sur la nouvelle interface ! <span aria-hidden={true}>🎉</span>
      </h2>

      <p className={styles['banner-description']}>
        Nous travaillons depuis quelques mois sur cette nouvelle version, pour
        vous proposer un outil plus pratique et plus agréable.
      </p>
      <p className={styles['banner-description']}>
        Nous continuons encore à l’améliorer : vous pouvez nous donner votre
        avis à n’importe quel moment depuis la bannière prévue à cet effet.
      </p>
      <div className={styles['banner-button']}>
        <Button onClick={() => setIsNewNavEnabled(false)}>Découvrir</Button>
      </div>
    </DialogBox>
  )
}
