import PropTypes from 'prop-types'
import React from 'react'

const CreateOffer = ({ titleId }) => (
  <>
    <h1 id={titleId}>Créer une offre</h1>
    <section className="tutorial-content">
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
      <p className="tco-italic">
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

CreateOffer.propTypes = {
  titleId: PropTypes.string.isRequired,
}

export default CreateOffer
