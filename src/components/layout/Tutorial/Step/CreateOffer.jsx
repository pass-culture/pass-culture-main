import React from 'react'

const CreateOffer = () => (
  <>
    <h1>
      {'Créer une offre'}
    </h1>
    <section className="tutorial-content">
      <div>
        {'Vous pouvez créer des offres numériques ou physiques de plusieurs façons :'}
      </div>
      <div>
        {
          "1. Automatiquement si vous utilisez un de nos logiciels partenaires (Titelive Stocks, GStocks, Librisoft, Praxiel, Allocine) ou êtes référencé sur l'une des plateformes partenaires (Placesdeslibraires.fr, leslibraires.fr ... et bien d'autres !)"
        }
      </div>
      <div className="tco-italic">
        {'Les offres sont synchronisés avec les données du gestionnaire  tous les soirs.'}
      </div>
      <div>
        <p>
          {'2. Manuellement avec notre système de création d’offre :'}
        </p>
        <ul>
          <li>
            {'- Séléctionner un type d’offre'}
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
