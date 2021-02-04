import React from 'react'

const CreateOffer = () => (
  <>
    <h1>
      {'Créer une offre'}
    </h1>
    <section className="tutorial-content">
      <p>
        {'Vous pouvez créer des offres numériques ou physiques de plusieurs façons :'}
      </p>
      <p>
        {
          "1. Automatiquement si vous utilisez un de nos logiciels partenaires (Titelive Stocks, GStocks, Librisoft, Praxiel, Allocine) ou êtes référencé sur l'une des plateformes partenaires (Placesdeslibraires.fr, leslibraires.fr ... et bien d'autres !)"
        }
      </p>
      <p className="tco-italic">
        {'Les offres sont synchronisées avec les données du gestionnaire tous les soirs.'}
      </p>
      <div>
        <p className="tco-no-margin">
          {'2. Manuellement avec notre système de création d’offre :'}
        </p>
        <ul>
          <li>
            {'- Sélectionner un type d’offre'}
          </li>
          <li>
            {'- Remplir les informations nécessaires'}
          </li>
          <li>
            {'- Ajouter une image'}
          </li>
        </ul>
      </div>
    </section>
  </>
)

export default CreateOffer
