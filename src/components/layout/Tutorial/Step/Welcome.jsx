import PropTypes from 'prop-types'
import React from 'react'

const Welcome = ({ titleId }) => (
  <>
    <h1 id={titleId}>
      {"Bienvenue dans l'espace acteurs culturels"}
    </h1>
    <section className="tutorial-content">
      <div className="tw-description">
        {
          'Le pass Culture est une politique culturelle publique permettant aux jeunes à partir de 18 ans de bénéficier d’une enveloppe de 500€ utilisable pour réserver vos offres.'
        }
      </div>
      <div className="tw-strong">
        {'Et pour ce faire, rien de plus simple !'}
      </div>
      <div className="tw-steps">
        <div>
          <p className="tw-numbers">
            {'1'}
          </p>
          <p>
            {'Renseigner vos coordonnées bancaires'}
          </p>
        </div>
        <div>
          <p className="tw-numbers">
            {'2'}
          </p>
          <p>
            {'Créer une offre physique ou numérique'}
          </p>
        </div>
        <div>
          <p className="tw-numbers">
            {'3'}
          </p>
          <p>
            {"Publier votre offre : elle sera visible sur l'application publique"}
          </p>
        </div>
        <div>
          <p className="tw-numbers">
            {'4'}
          </p>
          <p>
            {'Suivre et gérer vos réservations'}
          </p>
        </div>
      </div>
    </section>
  </>
)

Welcome.propTypes = {
  titleId: PropTypes.string.isRequired,
}

export default Welcome
