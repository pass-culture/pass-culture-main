import type { StoryObj } from '@storybook/react-vite'

import mockupPng from './mockup.png'
import { TipsBanner, type TipsBannerProps } from './TipsBanner'

export default {
  title: '@/ui-kit/TipsBanner',
  component: TipsBanner,
}

export const TipsBannerWithText: StoryObj<TipsBannerProps> = {
  args: {
    children:
      'Vous pouvez modifier la mise en forme de votre texte.Utilisez des doubles astérisques pour mettre en gras : **exemple** et des tirets bas pour l’italique : _exemple_Vous pourrez vérifier l’affichage à l’étape "Aperçu"',
  },
}

export const TipsBannerWithStructuredText: StoryObj<TipsBannerProps> = {
  args: {
    children: (
      <>
        <p>
          Quelques conseils pour rester en bonnes relations avec votre opossum
          domestiqué :
        </p>
        <br />
        <ul>
          <li>
            <strong>Ne pas le nourrir avec des aliments sucrés</strong> : les
            opossums sont sensibles aux aliments riches en sucre, ce qui peut
            entraîner des problèmes de santé.
          </li>
          <li>
            <strong>Éviter les interactions trop fréquentes</strong> : bien
            qu’ils soient sociables, les opossums ont besoin de temps seuls pour
            se reposer et se détendre.
          </li>
          <li>
            <strong>Fournir un espace sécurisé</strong> : assurez-vous que votre
            opossum a un endroit sûr où il peut se retirer s’il se sent menacé
            ou stressé.
          </li>
        </ul>
      </>
    ),
  },
}

export const TipsBannerWithLink: StoryObj<TipsBannerProps> = {
  args: {
    children:
      'Vous pouvez modifier la mise en forme de votre texte.Utilisez des doubles astérisques pour mettre en gras : **exemple** et des tirets bas pour l’italique : _exemple_Vous pourrez vérifier l’affichage à l’étape "Aperçu"',
  },
}

export const TipsBannerWithIllustration: StoryObj<TipsBannerProps> = {
  args: {
    children:
      'Vous pouvez modifier la mise en forme de votre texte.Utilisez des doubles astérisques pour mettre en gras : **exemple** et des tirets bas pour l’italique : _exemple_Vous pourrez vérifier l’affichage à l’étape "Aperçu"',
    decorativeImage: mockupPng,
  },
}
