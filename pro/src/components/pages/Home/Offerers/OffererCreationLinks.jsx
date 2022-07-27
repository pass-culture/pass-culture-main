import React from 'react'
import { Link } from 'react-router-dom'

const OffererCreationLinks = () => (
  <div
    className="h-card offerer-banner"
    data-testid="offerers-creation-links-card"
  >
    <div className="h-card-inner">
      <h3 className="h-card-title">Structures</h3>

      <div className="h-card-content">
        <p>
          Votre précédente structure a été supprimée. Pour plus d’informations
          sur la suppression et vos données, veuillez contacter notre support.
        </p>

        <div className="actions-container">
          <Link className="primary-link" to="/structures/creation">
            Ajouter une nouvelle structure
          </Link>
          <a
            className="secondary-link"
            href="mailto:support-pro@passculture.app"
          >
            Contacter le support
          </a>
        </div>
      </div>
    </div>
  </div>
)

export default OffererCreationLinks
