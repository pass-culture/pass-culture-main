import React from 'react'

import { IStepComponentProps } from '../types'

import styles from './Step.module.scss'

const CreateOffer = ({
  titleId,
  contentClassName,
}: IStepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Créer une offre</h1>
    <section className={contentClassName}>
      <p>
        Vous pouvez créer des offres numériques ou physiques de plusieurs façons
        :
      </p>
      <p>
        1. Automatiquement si vous utilisez un de nos logiciels partenaires
        (Titelive Stocks, GStocks, Librisoft, Praxiel) ou êtes référencé sur
        l’une des plateformes partenaires (Placesdeslibraires.fr,
        leslibraires.fr, Allociné ... et bien d’autres !)
      </p>
      <p className={styles['tco-italic']}>
        Les offres sont synchronisées avec les données du gestionnaire tous les
        soirs.
      </p>
      <div>
        <p>2. Manuellement avec notre système de création d’offre :</p>
        <ul>
          <li>Sélectionnez un type d’offre</li>
          <li>Remplissez les informations nécessaires</li>
          <li>Ajoutez une image</li>
        </ul>
      </div>
    </section>
  </>
)

export default CreateOffer
