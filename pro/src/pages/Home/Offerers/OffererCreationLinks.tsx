import React from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

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
          <ButtonLink
            variant={ButtonVariant.PRIMARY}
            link={{ isExternal: false, to: '/structures/creation' }}
          >
            Ajouter une nouvelle structure
          </ButtonLink>
          <ButtonLink
            variant={ButtonVariant.SECONDARY}
            link={{
              isExternal: true,
              to: 'mailto:support-pro@passculture.app',
            }}
          >
            Contacter le support
          </ButtonLink>
        </div>
      </div>
    </div>
  </div>
)

export default OffererCreationLinks
