import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'

import styles from './Declaration.module.scss'
import { EcoDesignLayout } from './EcoDesignLayout'

export const EcoDesignPolicy = () => {
  return (
    <EcoDesignLayout mainHeading="Politique d'écoconception au pass Culture">
      <div className={styles['page-content']}>
        <div className={styles['back-link']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="/ecoconception"
            icon={fullBackIcon}
            label="Retour vers la page déclaration d'écoconception"
          />
        </div>
        <h2 className={styles['heading2']}>Objectifs</h2>
        <p className={styles['paragraph']}>
          Le service{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://passculture.pro"
            isExternal
            label="passculture.pro"
          />{' '}
          s'inscrit dans une démarche d'écoconception visant à réduire ses
          impacts environnementaux. À cette fin, cette déclaration a été rédigée
          le 31 décembre 2025, dans le cadre de la mise en œuvre du référentiel
          général de l'écoconception des services numériques (version 2024).
        </p>
        <p className={styles['paragraph']}>
          Le référentiel général de l’écoconception des services numériques,
          document réalisé par l’Arcep et l’Arcom, en collaboration avec
          l’ADEME, la DINUM, la CNIL et l’Inria, est disponible sur le{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://www.arcep.fr/demarches-et-services/professionnels/referentiel-general-ecoconception-services-numeriques.html"
            isExternal
            label="site web de l’Arcep"
          />
        </p>
        <p className={styles['paragraph']}>
          Sa mise en œuvre poursuit quatre objectifs principaux&nbsp;:
        </p>
        <ol>
          <li className={styles['list-item']}>
            Concevoir des services numériques plus durables permettant d'
            <strong>allonger la durée de vie des terminaux</strong>
          </li>
          <li className={styles['list-item']}>
            Promouvoir une démarche de{' '}
            <strong>sobriété environnementale</strong> face aux stratégies de
            captation de l'attention de l'utilisateur pour des usages en ligne
            avec les objectifs environnementaux internationaux ;
          </li>
          <li className={styles['list-item']}>
            <strong>Diminuer les ressources</strong> informatiques mobilisées,
            optimiser le trafic de données et la sollicitation des
            infrastructures numériques ;
          </li>
          <li className={styles['list-item-spaced']}>
            Accroître le niveau de transparence sur l'empreinte environnementale
            du service numérique.
          </li>
        </ol>
        <p className={styles['paragraph']}>
          Le travail autour de l'écoconception du site{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://passculture.pro"
            isExternal
            label="passculture.pro"
          />{' '}
          s'inscrit dans la continuité de tout le travail qui a été fait et qui
          continue à être fait autour des questions d'accessibilité. Les
          éléments relatifs à ceux-ci sont disponibles dans la déclaration
          d'accessibilité, disponible via le lien{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://passculture.pro/accessibilite/declaration"
            isExternal
            label="https://passculture.pro/accessibilite/declaration"
          />
          .
        </p>
        <p className={styles['paragraph']}>
          Nous avons procédé à un audit interne. Nous sommes bien entendu à
          l’écoute de vos retours, remarques ou critiques concernant ce travail.
          Pour ce faire vous pouvez nous contacter directement à l'adresse mail{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="mailto:eco-conception@passculture.app"
            isExternal
            label="eco-conception@passculture.app"
          />
          .
        </p>
        <h2 className={styles['heading2']}>
          Score d’avancement dans la mise en œuvre du référentiel
        </h2>
        <p>Score d’avancement au 31 décembre 2025 : 69%.</p>
        <p>Score d’avancement précédent : première publication.</p>
        <p className={styles['paragraph']}>
          Le service numérique{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://passculture.pro"
            isExternal
            label="passculture.pro"
          />{' '}
          vise une amélioration de ce score sur les prochaines années. Pour ce
          faire, des revues et audits seront réalisés tous les ans.
        </p>
        <h2 className={styles['heading2']}>
          Plan d'avancement dans la démarche d'écoconception du service
          numérique
        </h2>
        <p className={styles['paragraph']}>
          Ceci constitue la première déclaration d'écoconception du pass
          Culture. Cette déclaration pâtit d'un manque de mesure sur plusieurs
          aspects. Dans ce cadre, la première démarche engagée sera de :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Sensibiliser et former l'ensemble du pôle Produit / Technique aux
            enjeux de l'écoconception et aux bonnes pratiques de développement
          </li>
          <li className={styles['list-item']}>
            Utiliser l'outil EcoIndex sur les parcours critiques du site
          </li>
          <li className={styles['list-item']}>
            Diminuer le poids du bundle pour limiter le nombre d'appels HTTP
          </li>
          <li className={styles['list-item-spaced']}>
            Réaliser une analyse du cycle de vie (ACV)
          </li>
        </ul>
        <p className={styles['paragraph']}>
          En outre, l'hébergement étant un point crucial pour limiter l'impact
          du service, nous avons prévu de migrer nos data center en France
          hexagonale.
        </p>
        <p className={styles['paragraph']}>
          D'autre part, les pistes d'actions suivantes sont ou seront mises en
          place :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Accentuer la veille sur l'écoconception
          </li>
          <li className={styles['list-item']}>
            Obtenir le label Numérique Responsable
          </li>
          <li className={styles['list-item']}>
            Diminuer le nombre d'appels entre le frontend et le backend et les
            optimiser
          </li>
          <li className={styles['list-item-spaced']}>
            Établir une feuille de route pluriannuelle d'améliorations
            techniques afin de réduire l'empreinte carbone et hydrique des
            parcours critiques de l’Espace Partenaires en se basant sur les
            mesures effectuées par l’EcoIndex
          </li>
        </ul>
        <h3 className={styles['heading3']}>
          Chemins critiques et unités fonctionnelles évalués avec le référentiel
        </h3>
        <p className={styles['paragraph']}>
          A l’heure actuelle, aucun diagnostic n’a été fait. Les chemins
          critiques seront définis lors de la mise en place de l’outil EcoIndex.
        </p>
        <h3 className={styles['heading3']}>
          Référent en écoconception numérique
        </h3>
        <p className={styles['paragraph']}>
          Une personne est nommée référente écoconception numérique en interne.
          Vous pouvez la contacter à l’adresse suivante{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="mailto:eco-conception@passculture.app"
            isExternal
            label="eco-conception@passculture.app"
          />
        </p>
      </div>
    </EcoDesignLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = EcoDesignPolicy
