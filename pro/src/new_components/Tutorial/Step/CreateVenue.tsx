import { IStepComponentProps } from '../types'
import React from 'react'

const CreateVenue = ({
  titleId,
  contentClassName,
}: IStepComponentProps): JSX.Element => (
  <>
    <h1 id={titleId}>Gérer vos lieux culturels</h1>
    <section className={contentClassName}>
      <p>
        Les lieux vous permettent de créer des offres physiques et de les rendre
        visibles sur l’application publique.
      </p>
      <p>
        Vous pouvez créer dans vos lieux des évènements, des visites, des offres
        pour des livres, des instruments de musique, etc.
      </p>
      <p>
        Pour les offres dématérialisées (livres numériques, visites virtuelles,
        adaptations de spectacles, jeux vidéos, etc.), pas besoin de créer un
        lieu, il vous suffit de créer une nouvelle offre numérique.
      </p>
      <p>
        Pour créer un lieu physique, vous devez renseigner certaines
        informations (adresse, type, etc.).
      </p>
    </section>
  </>
)

export default CreateVenue
