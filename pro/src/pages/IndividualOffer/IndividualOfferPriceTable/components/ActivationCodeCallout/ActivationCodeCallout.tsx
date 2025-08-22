import { FormLayoutDescription } from '@/components/FormLayout/FormLayoutDescription'

import styles from './ActivationCodeCallout.module.scss'

export const ActivationCodeCallout = () => (
  <FormLayoutDescription
    className={styles['box']}
    description={
      <div>
        <p>
          Pour ajouter des codes d’activation, veuillez passer par le bouton et
          choisir l’option correspondante.
        </p>
      </div>
    }
    links={[
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4411991970705--Acteurs-culturels-Comment-cr%C3%A9er-une-offre-num%C3%A9rique-avec-des-codes-d-activation',
        isExternal: true,
        label: 'Comment gérer les codes d’activation ?',
        target: '_blank',
      },
    ]}
    isBanner
  />
)
