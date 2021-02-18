import PropTypes from 'prop-types'
import React from 'react'

const CreateVenue = ({ titleId }) => (
  <>
    <h1 id={titleId}>
      {'Gérer vos lieux culturels'}
    </h1>
    <section className="tutorial-content cv-content">
      <p>
        {'Ces lieux vous permettent de géolocaliser les offres visibles dans l’application.'}
      </p>
      <div>
        <p>
          {'Ils sont de deux types :'}
        </p>
        <ul>
          <li className="cv-venue-creation">
            <p>
              {
                'Numérique : pour vos offres dématérialisées (livres numériques, visites virtuelles, captations de spectacles, jeux vidéos, etc.).'
              }
            </p>
            <p>
              {'Votre lieu numérique est créé par défaut.'}
            </p>
          </li>
          <li>
            {
              'Physique : pour les événements, les visites, les livres, les instruments de musique, etc.'
            }
          </li>
        </ul>
      </div>
    </section>
  </>
)

CreateVenue.propTypes = {
  titleId: PropTypes.string.isRequired,
}

export default CreateVenue
