import { DialogBox } from 'components/DialogBox/DialogBox'
import { Button } from 'ui-kit/Button/Button'

import topImage from './assets/new-banner-beta.svg'
import styles from './WelcomeToTheNewBetaBanner.module.scss'

type WelcomeToTheNewBetaBannerProps = {
  onDismiss(): void
  onContinue(): void
}
export const WelcomeToTheNewBetaBanner = ({
  onDismiss,
  onContinue,
}: WelcomeToTheNewBetaBannerProps): JSX.Element => {
  return (
    <DialogBox
      labelledBy="welcome-on-new-interface"
      hasCloseButton={true}
      onDismiss={onDismiss}
      extraClassNames={styles['banner']}
      closeButtonClassName={styles['banner-close']}
    >
      <div className={styles['banner-image']}>
        <img src={topImage} alt="Nouvelle interface" />
      </div>
      <h2 id="welcome-on-new-interface" className={styles['banner-title']}>
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
        <Button onClick={onContinue}>Découvrir</Button>
      </div>
    </DialogBox>
  )
}
