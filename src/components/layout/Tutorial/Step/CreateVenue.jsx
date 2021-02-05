import PropTypes from 'prop-types'
import React from 'react'

const CreateVenue = ({ titleId }) => (
  <>
    <h1 id={titleId}>
      {'Gérer vos lieux culturels'}
    </h1>
    <section className="tutorial-content">
      <p>
        {
          'Les lieux vous permettent de créer des offres et de les rendre visibles sur l’application publique.'
        }
      </p>
      <div>
        <p className="tco-no-margin">
          {'Ils sont de deux types :'}
        </p>
        <ul>
          <li>
            {
              'Numérique : pour vos offres dématérialisées (livre numérique, visites virtuelles, captations de spectacles, jeux vidéos, etc.)'
            }
          </li>
          <li>
            {
              'Physique : pour les événements, les visites, les livres, instruments de musique, etc.'
            }
          </li>
        </ul>
      </div>
      <p>
        {'Votre lieu numérique est créé par défaut dans votre espace acteurs culturels.'}
      </p>
      <p>
        {
          'Pour créer un lieu physique, vous devez renseigner certaines informations (adresse, type, etc).'
        }
      </p>
    </section>
  </>
)

CreateVenue.propTypes = {
  titleId: PropTypes.string.isRequired,
}

export default CreateVenue
