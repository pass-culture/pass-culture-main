import cn from 'classnames'
import { useState } from 'react'

import { ASSETS_BUCKET_URL } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullBackIcon from '@/icons/full-back.svg'
import fullDownIcon from '@/icons/full-down.svg'
import fullDownloadIcon from '@/icons/full-download.svg'
import fullUpIcon from '@/icons/full-up.svg'

import styles from './Declaration.module.scss'
import { nonValidatedCriteria, validatedCriteria } from './declarationCriteria'
import { EcoDesignLayout } from './EcoDesignLayout'

export const EcoDesignDeclaration = () => {
  const [isValidatedCriteriaOpen, setIsValidatedCriteriaOpen] = useState(false)
  const [isNonValidatedCriteriaOpen, setIsNonValidatedCriteriaOpen] =
    useState(false)

  return (
    <EcoDesignLayout mainHeading="Déclaration RGESN">
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
        <h2 className={styles['heading2']}>
          Détails du diagnostic avec le référentiel général de l’écoconception
          des services numériques
        </h2>
        <div className={styles['download-button']}>
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to={`${ASSETS_BUCKET_URL}/assets/declaration-rgesn-pass-culture.pdf`}
            icon={fullDownloadIcon}
            label="Télécharger la déclaration RGESN de l'espace partenaires"
            isExternal
            opensInNewTab
          />
        </div>

        <div className={styles['accordion-button']}>
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={() => setIsValidatedCriteriaOpen(!isValidatedCriteriaOpen)}
            icon={isValidatedCriteriaOpen ? fullUpIcon : fullDownIcon}
            label="Critères validés (ou non applicables) par le service numérique"
          />
        </div>
        <div>
          {isValidatedCriteriaOpen && (
            <>
              <p>Numérotation des fiches pratiques des critères validés :</p>
              <ul className={styles['criteria-list']}>
                {validatedCriteria.map((criterion) => (
                  <li key={criterion} className={styles['list-item']}>
                    {criterion}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div
          className={cn(styles['accordion-button'], {
            [styles['non-validated-button-closed']]:
              !isNonValidatedCriteriaOpen,
          })}
        >
          <Button
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={() =>
              setIsNonValidatedCriteriaOpen(!isNonValidatedCriteriaOpen)
            }
            icon={isNonValidatedCriteriaOpen ? fullUpIcon : fullDownIcon}
            label="Critères non validés (ou en cours) par le service numérique"
          />
        </div>
        <div>
          {isNonValidatedCriteriaOpen && (
            <>
              <p>
                Numérotation des fiches pratiques des critères non validés :
              </p>
              <ul className={styles['criteria-list']}>
                {nonValidatedCriteria.map((criterion) => (
                  <li key={criterion} className={styles['list-item']}>
                    {criterion}
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <h3 className={styles['heading3']}>1. Stratégie</h3>

        <p className={styles['body-accent']}>
          Évaluation de l’utilité du service, en tenant compte de ses impacts
          environnementaux
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 1.1 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service a été évalué favorablement en termes d’utilité. En effet,
          le service est la mise en œuvre d’une politique publique pour rendre
          accessible la culture aux jeunes. Il s’inscrit plus globalement dans
          l’objectif de développement durable numéro 4 - Assurer à tous une
          éducation équitable, inclusive et de qualité et des possibilités
          d’apprentissage tout au long de la vie.
        </p>

        <p className={styles['body-accent']}>
          Cibles utilisatrices de l'espace partenaires du pass Culture
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 1.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Les cibles utilisatrices du service ont été identifiées en procédant à
          une analyse des textes réglementaires et de nombreux ateliers de
          co-construction avec les utilisateurs et utilisatrices.
        </p>
        <p className={styles['paragraph']}>
          Ainsi, les cibles utilisatrices du service sont les acteurs culturels.
        </p>
        <p className={styles['paragraph']}>
          En cohérence, le service numérique répond à leurs besoins puisque
          présentant les fonctionnalités suivantes : s’enregistrer sur la
          plateforme, proposer des offres auprès des jeunes bénéficiaires, des
          enseignants, suivre ses réservations, retrouver ses remboursements et
          proposer des actions de médiation.
        </p>

        <p className={styles['body-accent']}>
          Référent en écoconception numérique
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 1.3 - Validé</em>
        </p>
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

        <p className={styles['body-accent']}>
          Empreinte environnementale du service
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 1.4, 1.5 - En cours</em>
        </p>
        <p className={styles['paragraph']}>
          L’empreinte environnementale du service n’a pas encore été évaluée. Un
          référent en écoconception a été formé au cours de l’année 2024 pour
          mener des ACV, ainsi que pour mener des projets d’écoconception et
          l’appliquer à l’infrastructure et au backend. Nous planifions en 2026
          une certification NR.
        </p>

        <p className={styles['body-accent']}>Données et licence</p>
        <p className={styles['paragraph']}>
          <em>• critère 1.6, 1.7, 1.8, 1.9, 1.10 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique collecte des données afin de répondre aux besoins
          de fonctionnement ou au débugging. Il ne comporte pas de collecte de
          métadonnées à des fins publicitaires. La politique de gestion des
          cookies est publiée directement sur le site.
        </p>
        <p className={styles['paragraph']}>
          Afin d’assurer la sécurité des données du service et répondre aux
          enjeux du RGS, des mécanismes cryptographiques sont mis en place.
        </p>
        <p className={styles['paragraph']}>
          Le service numérique publie une partie de son code en opensource, sous
          la licence MPL-2.0 :{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://github.com/pass-culture/pass-culture-main"
            isExternal
            opensInNewTab
            label="https://github.com/pass-culture/pass-culture-main"
          />
        </p>
        <p className={styles['paragraph']}>
          Les langages de développement de l'espace partenaires sont des
          langages standards et généralistes : Python et React. Une API Rest
          largement documentée est disponible pour interfacer le service avec
          d’autres.
        </p>

        <h3 className={styles['heading3']}>2. Spécifications</h3>

        <p className={styles['body-accent']}>
          Configuration matérielle minimum pour accéder au service
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.1, 2.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique, sans avoir constitué une liste exhaustive des
          matériels pour y accéder, est utilisable sur d’anciens types de
          terminaux.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.3 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Pas de connexion internet minimum : la rapidité du service dépendra de
          la puissance de la connexion.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.4, 2.5 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique s’appuie sur un affichage dynamique. Nous avons
          revu toute l’interface en 2024 pour qu’elle soit responsive afin de
          répondre aux enjeux d’accessibilité et d’écoconception.
        </p>
        <p className={styles['paragraph']}>
          Type d’interfaces minimum compatibles :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Desktop Chrome, Edge, Opera, Firefox et Mobile Chrome sur leur 3
            dernières versions
          </li>
          <li className={styles['list-item']}>
            Desktop Safari, Mobile Safari sur les 2 dernières versions
          </li>
        </ul>
        <p className={styles['paragraph']}>
          Tailles d’affichage supportées par le service : responsive (mobile,
          tablet, laptop)
        </p>
        <p className={styles['paragraph']}>
          Détail des tests réalisés : cf. la déclaration d’accessibilité.
        </p>

        <p className={styles['body-accent']}>
          Stratégie de conception, maintenance et décommissionnement
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.6 - Non validé</em>
        </p>
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
          n'a pas procédé à une revue de code et de conception pour réduire le
          coût environnemental du service.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.7 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Cependant, les fonctionnalités du service sont adaptées de façon
          dynamique dans le cadre de la politique de maintenance et de
          décommissionnement mise en œuvre pour assurer l’adéquation entre ces
          fonctionnalités et les besoins utilisateurs : nous recueillons depuis
          la plateforme les besoins et problématiques des utilisateurs et
          utilisatrices pour faire évoluer le service en fonction de leurs
          besoins. Nous supprimons également des fonctionnalités qui ne sont
          plus utilisées ou pas assez largement adoptées.
        </p>

        <p className={styles['body-accent']}>Fournisseurs</p>
        <p className={styles['paragraph']}>
          <em>• critère 2.8 - En cours</em>
        </p>
        <p className={styles['paragraph']}>
          Les fournisseurs issus des marchés publics sont tenus de respecter
          certains engagements environnementaux à travers des critères ou des
          clauses RSE allant de 5% à 15%. Cependant, ils ne garantissent pas
          forcément une démarche de réduction de leurs impacts environnementaux
          : ces engagements peuvent par exemple être sociaux.
        </p>

        <p className={styles['body-accent']}>
          Composants d’interface prêts à l’emploi utilisés
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.9 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique repose sur un Design System accessible qui permet
          la réutilisation des composants. En 2026, nous allons travailler à
          l’analyse de ce Design System au regard des enjeux environnementaux.
        </p>

        <p className={styles['body-accent']}>
          Liste des services tiers utilisés par le service
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 2.10 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique repose sur les services tiers suivants :
        </p>
        <ul>
          <li className={styles['list-item']}>ReCaptcha</li>
          <li className={styles['list-item']}>Youtube</li>
        </ul>
        <p className={styles['paragraph']}>
          Ces services ne proposent pas de déclaration RGESN ou autre politique
          d’écoconception. Cependant, une migration du service de captcha sera
          effectuée en 2026 et les critères du numérique responsable, dont
          l'accessibilité, la sécurité, la confidentialité et l'écoconception
          seront pris en compte.
        </p>

        <h3 className={styles['heading3']}>3. Architecture</h3>

        <p className={styles['body-accent']}>
          Choix d’architecture et de composants
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 3.1 - Non applicable</em>
        </p>
        <p className={styles['paragraph']}>
          Le développement du backend et frontend du service numérique repose
          sur le(s) framework React, Python et PostgreSQL. Il est donc de la
          responsabilité des équipes techniques d’appliquer les bonnes pratiques
          d’écoconception pour réduire leurs impacts environnementaux.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 3.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le nombre de serveurs que le service numérique utilise augmente et
          diminue automatiquement selon les variations de la consommation des
          ressources observées (la charge), donc en fonction des besoins du
          service.
        </p>
        <p className={styles['paragraph']}>
          Ces variations ont permis d’encadrer une limite haute et une limite
          basse :
        </p>
        <p className={styles['paragraph']}>
          Limite basse : le nombre minimum qui permet de garder le service up (2
          serveurs).
        </p>
        <p className={styles['paragraph']}>
          Limite haute : observation au fil du temps en termes d’utilisation des
          ressources ou d’erreurs que pouvaient rencontrer les utilisateurs.
        </p>

        <p className={styles['body-accent']}>Protocoles d’échange utilisés</p>
        <p className={styles['paragraph']}>
          <em>• critère 3.3 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Afin de prévenir les risques d’obsolescence et de limiter le besoin en
          mise à jour ou modernisation, le service numérique repose sur des
          protocoles pérennes et adaptés à ses fonctionnalités. En particulier :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Le service numérique est accessible en IPV6 (et en IPV4)
          </li>
          <li className={styles['list-item']}>
            Le service numérique repose sur le protocole HTTPS
          </li>
          <li className={styles['list-item-spaced']}>
            La version de TLS utilisée doit prendre en charge la version la plus
            récente (TLS v1.3)
          </li>
        </ul>

        <p className={styles['body-accent']}>Mise à jour</p>
        <p className={styles['paragraph']}>
          <em>• critère 3.4, 3.5, 3.6 - Non applicable</em>
        </p>
        <p className={styles['paragraph']}>
          Nous sommes un service web, nous suivons les mises à jour de framework
          et nous ne sommes pas liés à des configurations d’OS mobile ou PC.
        </p>

        <p className={styles['body-accent']}>
          Environnements de développement, de préproduction ou de test
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 3.7 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Les environnements de développement, de préproduction ou de test sont
          désactivés la nuit, sur les plages horaires où ils sont inutilisés. Le
          service numérique utilise des environnements de développement, de
          préproduction ou de test mutualisés.
        </p>

        <h3 className={styles['heading3']}>
          4. Expérience et interface utilisateur
        </h3>

        <p className={styles['body-accent']}>UX/UI</p>
        <p className={styles['paragraph']}>
          <em>• critère 4.1 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Nous ne proposons aucun contenu en lecture automatique ni aucune
          animation visuelle de plus de 4 secondes.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Nous ne proposons aucun contenu en défilement infini. Les principaux
          composants sont paginés.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.3 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service est designé par une équipe de Product Designers qui
          utilisent diverses méthodologies pour adapter le service aux usages.
          Nous récoltons en continu les avis des usagers pour prévoir les
          futures évolutions du service. Nous utilisons également un outil
          d’analyse quantitative des parcours afin d’identifier des
          incohérences.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.4 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Oui, tel que décrit dans la politique de gestion des cookies.
        </p>

        <p className={styles['body-accent']}>Composants</p>
        <p className={styles['paragraph']}>
          <em>• critère 4.5 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Utilisation du framework React, surcouche de Typescript.
        </p>

        <p className={styles['body-accent']}>Contenus audiovisuels et animés</p>
        <p className={styles['paragraph']}>
          <em>• critère 4.6 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique n’intègre pas de contenu vidéo, audio et animé à
          titre purement décoratif. Il est cependant proposé aux utilisateurs
          d’ajouter des vidéos sur leurs offres afin de mieux contextualiser
          leur proposition auprès des jeunes.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.7 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          En cohérence avec les cibles utilisatrices identifiées et l’impact
          environnemental différencié des contenus audiovisuels, les choix
          suivants de recours au texte, à l’image, l’audio ou la vidéo ont été
          effectués : les vidéos n’ont été proposées que parce que ce type de
          contenu est plébiscité par les jeunes utilisateurs et qu’il leur
          permet de mieux découvrir les contenus culturels.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.8 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service propose 1 police déclinée en 5 épaisseurs et 7 tailles.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.9 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Nous ne proposons pas de désactiver l'autocomplétion de saisie des
          caractères lors des recherches d’offres ou de réservations.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.10 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Nous informons systématiquement l’utilisateur ou l’utilisatrice des
          formats de saisie attendus avant la soumission du formulaire. Ceux-ci
          sont validés en front avant soumission.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.11, 4.12 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>Non.</p>
        <p className={styles['paragraph']}>
          <em>• critère 4.13 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service par défaut prévoit des notifications rédigées par notre
          service marketing à travers des newsletters ciblées ou des contenus
          proposé directement dans le service{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://passculture.pro"
            isExternal
            label="passculture.pro"
          />{' '}
          à raison de 2 ou 3 informations mensuelles.
        </p>
        <p className={styles['paragraph']}>
          L’utilisateur a bien la possibilité de désactiver ou de réduire les
          notifications du service en acceptant ou non les cookies et en
          s’abonnant / se désabonnant à la newsletter.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 4.14 - Validé</em>
        </p>
        <p className={styles['paragraph']}>Aucun dark pattern.</p>
        <p className={styles['paragraph']}>
          <em>• critère 4.15 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>Non.</p>

        <h3 className={styles['heading3']}>5. Contenus</h3>

        <p className={styles['paragraph']}>
          <em>• critère 5.1 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique met en œuvre des principes d’écoconception pour
          diminuer dès que possible le poids des contenus audiovisuels qu’il
          intègre. Les éléments suivants font état des principaux périmètres
          définis pour minimiser l’empreinte environnementale des images, vidéos
          et de l’audio sur lequel repose le service.
        </p>

        <p className={styles['body-accent']}>Images</p>
        <p className={styles['paragraph']}>
          <em>• critère 5.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Les images sont miniaturisées et sont sauvegardées dans un dossier de
          stockage du cloud. La version originale est également conservée. La
          résolution minimale attendue est de 400x600 px et le poids maximal est
          de 10 Mo.
        </p>

        <p className={styles['body-accent']}>Contenus vidéo</p>
        <p className={styles['paragraph']}>
          <em>• critère 5.3, 5.4 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Nous ne stockons aucune vidéo mais uniquement les URLs et les
          métadonnées en provenance des plateformes hébergeant les vidéos.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 5.5 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Pas de fonctionnement "écoute seule".
        </p>

        <p className={styles['body-accent']}>Audio - non applicable</p>
        <p className={styles['paragraph']}>
          <em>• critère 5.6 - Non applicable</em>
        </p>

        <p className={styles['body-accent']}>Documents</p>
        <p className={styles['paragraph']}>
          <em>• critère 5.7 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Les documents téléchargeables sont des PDF ou des fichiers Excel. Les
          utilisateurs peuvent spécifier les informations qu’ils souhaitent
          télécharger afin de réduire la taille des fichiers.
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 5.8 - 7.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Une fonctionnalité d’archivage est mise à disposition des utilisateurs
          et utilisatrices pour les offres collectives. Les offres individuelles
          sont archivées automatiquement en fonction de leur activité.
        </p>

        <h3 className={styles['heading3']}>6. Frontend – 7 Backend</h3>

        <p className={styles['body-accent']}>Limites de poids et de requêtes</p>
        <p className={styles['paragraph']}>
          <em>• critère 6.1 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Nous n’avons pas mis en place de mesure à l’heure actuelle. La mise en
          place de l’EcoIndex nous permettra de définir une stratégie en la
          matière.
        </p>

        <p className={styles['body-accent']}>Stratégie de mise en cache</p>
        <p className={styles['paragraph']}>
          <em>• critère 6.2, 7.1 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le service numérique a mis en place une stratégie de cache, optimisée
          au regard du type de contenu, du contexte d’application et des
          scénarios d’usage. En voici les principaux contours :
        </p>
        <p className={styles['paragraph']}>
          Côté client : on utilise le cache au maximum pour éviter de répéter
          plusieurs fois les mêmes requêtes (mutation de cache).
        </p>
        <p className={styles['paragraph']}>
          Côté backend : utilisation du cache pour traiter les informations
          asynchrones.
        </p>

        <p className={styles['body-accent']}>
          Compression des ressources transférées
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 6.3 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 6.4, 6.5 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 6.6 - Non applicable</em>
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 6.7 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          L'ensemble des ressources ne prend actuellement en charge que le
          protocole HTTP/1.
        </p>

        <h3 className={styles['heading3']}>7. Backend</h3>

        <p className={styles['paragraph']}>
          <em>• critère 7.1 - Validé (cf 6.2)</em>
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 7.2 - Validé (cf 5.8)</em>
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 7.3 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Pas d’information de traitement de données en asynchrone
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 7.4 - Non applicable</em>
        </p>

        <h3 className={styles['heading3']}>8. Hébergement</h3>

        <p className={styles['paragraph']}>
          Nom du fournisseur ou prestataire d’hébergement physique des serveurs
          (de stockage ou de calcul notamment) pour permettre de suivre les
          impacts environnementaux de l’hébergement : Centre de données Google
          de Saint-Ghislain/Mons, en Belgique.
        </p>

        <p className={styles['body-accent']}>
          Engagements écologiques de l'hébergeur
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.1 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          L’hébergement du service est assuré par Google Cloud Platform (GCP) –
          Google LLC, États-Unis. Cet hébergeur est signataire du Code de
          Conduite sur les Datacentres.
        </p>
        <p className={styles['paragraph']}>
          Il a par ailleurs pris les engagements suivants pour diminuer son
          empreinte environnementale :{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://sustainability.google/intl/fr_fr/operations/net-zero-carbon/"
            isExternal
            opensInNewTab
            label="https://sustainability.google/intl/fr_fr/operations/net-zero-carbon/"
          />
        </p>

        <p className={styles['paragraph']}>
          <em>• critère 8.2 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Afin de diminuer l’impact environnemental des équipements nécessaires
          à l’hébergement, les actions suivantes ont été entreprises :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Communication sur la durée de vie moyenne de son parc d’équipements
            : Google conçoit ses propres serveurs et équipements et les
            maintient en service pour une durée moyenne de 6 ans (contre 3 à 5
            ans dans le secteur), avant d’être réutilisés ou recyclés ;
          </li>
          <li className={styles['list-item']}>
            Informations sur l’impact environnemental de l’achat de ces
            équipements : Google travaille à l’intégration de matériaux
            circulaires (matières premières recyclées) dans les serveurs et
            autres produits. L’objectif est de maximiser l’utilisation de
            matériaux recyclés dans les produits et emballages d’ici 2025 ;
          </li>
          <li className={styles['list-item']}>
            Politique d’achat durable : Google privilégie l’achat d’équipements
            de réseau et de stockage conçus pour l’efficacité énergétique et la
            durabilité. L’entreprise travaille avec ses fournisseurs pour
            réduire l’empreinte carbone des produits qu’elle achète ;
          </li>
          <li className={styles['list-item']}>
            Actions pour optimiser la phase d’usage des équipements : Conception
            sur mesure des serveurs : Les serveurs Google sont conçus pour
            s’adapter à leur charge de travail, ce qui réduit la consommation
            d’énergie inactive. Gestion de l’IA/ML : Utilisation de l’IA pour
            optimiser les charges de travail et le refroidissement.
            Virtualisation : Maximisation de l’utilisation des ressources via la
            virtualisation (GCP) ;
          </li>
          <li className={styles['list-item-spaced']}>
            Actions pour optimiser la fin de vie des équipements (recyclage,
            réutilisation, reconditionnement) : Google a des programmes de
            réutilisation et de recyclage qui gèrent 100 % des équipements hors
            service. L’objectif est la réutilisation des composants (disques
            durs, mémoires, processeurs) ou leur recyclage si la réutilisation
            n’est pas possible ;
          </li>
        </ul>

        <p className={styles['body-accent']}>
          Efficacité environnementale de l’hébergement du service
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.3 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          L’hébergement fournit les indicateurs suivants sur son efficacité
          énergétique et d’utilisation d’eau :
        </p>
        <ul>
          <li className={styles['list-item-spaced']}>
            PUE (Power Usage Effectiveness) réel : 1,08
          </li>
        </ul>
        <p className={styles['paragraph']}>
          <em>• critère 8.4 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>
          Google ne publie pas le WUE (Water Usage Effectiveness) réel par
          campus individuel, mais seulement la moyenne mondiale (1,34 en 2023).
          La consommation réelle de 1,4 million de m³ d'eau (non potable) en
          2023 est la donnée la plus précise disponible pour Saint-Ghislain.
        </p>

        <p className={styles['body-accent']}>
          Documentation sur l’origine de l’électricité consommée
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.5 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Le mix énergétique de l’hébergement du service numérique est documenté
          et présente une consommation d’énergie renouvelable majoritaire comme
          l’attestent les données suivantes :
        </p>
        <p className={styles['paragraph']}>
          Quantité annuelle d’énergie contractualisée : 100 % de l’énergie
          consommée est couverte par des achats d’énergie renouvelable (PPA ou
          Garanties d’Origine), garantissant une couverture de 100 % de
          l’électricité consommée par des énergies renouvelables annuellement :
        </p>
        <ul>
          <li className={styles['list-item']}>
            Part de PPA sur le réseau français, mais hors site : Google ne
            publie pas la ventilation des PPA par campus/région. On sait que des
            PPA sont signés en Belgique.
          </li>
          <li className={styles['list-item']}>
            Part autoconsommation (potentiellement par PPA ou support complet
            des coûts de capital et autres) : 2,9 GWh/an (selon le gestionnaire
            de réseau local IDEA).
          </li>
          <li className={styles['list-item']}>
            Part des garanties d'origine : Non publiée.
          </li>
          <li className={styles['list-item']}>
            REF (Renewable Energy Factor) : Google ne publie pas le REF de la
            même manière que la France, mais son indicateur clé, la Carbon-Free
            Energy (CFE), indique que 64 % de l’électricité consommée est sans
            carbone 24/7 à l’échelle mondiale.
          </li>
          <li className={styles['list-item-spaced']}>
            Part d'énergie bas carbone : 0 % (Google est neutre en carbone et
            compense la totalité de l’énergie non couverte par le CFE 24/7 par
            l’achat de crédits carbone de haute qualité et de garanties
            d’origine).
          </li>
        </ul>

        <p className={styles['body-accent']}>Localisation de l’hébergement</p>
        <p className={styles['paragraph']}>
          <em>• critère 8.6 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          L’hébergement du service est situé en Belgique.
        </p>
        <p className={styles['paragraph']}>
          L’intensité carbone du mix énergétique du pays où sont localisés
          l’hébergement est estimé à 158 CO₂eq/kWh. Il s’agit d’une valeur
          conforme à la trajectoire SBTi (Science-based Targets Initiative) de
          réduction des émissions de gaz à effet de serre requise par l’accord
          de Paris. L’hébergement du service a pour objectif d’être déplacé en
          France à horizon 2026.
        </p>

        <p className={styles['body-accent']}>
          Réutilisation de la chaleur fatale
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.7 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          Ce critère est validé car le PUE de l’hébergeur est inférieur ou égal
          à 1,2 (1,08)
        </p>

        <p className={styles['body-accent']}>
          Données "chaudes" et "froides" hébergées distinctement
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.8 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>Non.</p>

        <p className={styles['body-accent']}>
          Duplication des données lorsque nécessaire
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.9 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>Non.</p>

        <p className={styles['body-accent']}>
          Décalage des calculs et mises à jour asynchrones
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 8.10 - Non validé</em>
        </p>
        <p className={styles['paragraph']}>Non.</p>

        <h3 className={styles['heading3']}>9. Algorithmie - Non applicable</h3>

        <p className={styles['body-accent']}>
          Justification de la phase d’entraînement
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 9.1 - Validé</em>
        </p>
        <p className={styles['paragraph']}>
          L'inclusion d'une phase d'entraînement pour le service numérique{' '}
          <Button
            as="a"
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            to="https://passculture.pro"
            isExternal
            label="passculture.pro"
          />{' '}
          a été envisagée et n'a pas été jugée nécessaire.
        </p>

        <p className={styles['body-accent']}>
          Phase d’entraînement - Non applicable
        </p>
        <p className={styles['paragraph']}>
          <em>• critère 9.2, 9.3, 9.4, 9.5, 9.6, 9.7 - Non applicable</em>
        </p>
        <p className={styles['paragraph']}>
          Non applicable car il n’y a pas de phase d’entraînement.
        </p>
      </div>
    </EcoDesignLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = EcoDesignDeclaration
