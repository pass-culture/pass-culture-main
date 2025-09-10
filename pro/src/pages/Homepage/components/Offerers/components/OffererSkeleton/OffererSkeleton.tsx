import { Card } from '@/components/Card/Card'
import { Skeleton } from '@/ui-kit/Skeleton/Skeleton'

import styles from './OffererSkeleton.module.scss'

export function OffererSkeleton(): JSX.Element {
  return (
    <section className={styles.page} aria-busy="true" aria-live="polite">
      {/* H1 + intro */}
      <Skeleton height="2rem" width="40%" />
      <Skeleton height="1rem" width="90%" />
      <Skeleton height="1rem" width="80%" />

      {/* Carte partenaire */}
      <Card aria-busy="true" aria-live="polite">
        {/* bloc image + infos principales */}
        <div className={styles.header}>
          {/* Image */}
          <div className={styles.image}>
            <Skeleton height="180px" width="100%" margin="0" />
          </div>

          {/* Infos */}
          <div className={styles.main}>
            {/* sur-titre (ex: CINÉMA - SALLE DE PROJECTIONS) */}
            <Skeleton height="0.875rem" width="45%" />

            {/* Titre (ex: Herbert Marcuse Entreprise - Salle 1) */}
            <Skeleton height="1.5rem" width="85%" />

            {/* Adresse */}
            <Skeleton height="1rem" width="60%" />

            <Skeleton height="1rem" width="50%" />
          </div>
        </div>

        {/* Section Grand public */}
        <section className={styles.section}>
          <Skeleton height="1rem" width="20%" /> {/* Titre section */}
          <ul className={styles.list} aria-hidden>
            <li className={styles.listItem}>
              <Skeleton height="1rem" width="1rem" roundedFull />
              <Skeleton height="1rem" width="45%" margin="0 0 0 0.5rem" />
            </li>
            <li className={styles.listItem}>
              <Skeleton height="1rem" width="1rem" roundedFull />
              <Skeleton height="1rem" width="50%" margin="0 0 0 0.5rem" />
            </li>
            <li className={styles.listItem}>
              <Skeleton height="1rem" width="1rem" roundedFull />
              <Skeleton height="1rem" width="35%" margin="0 0 0 0.5rem" />
            </li>
          </ul>
        </section>
      </Card>
    </section>
  )
}
