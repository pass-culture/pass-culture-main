import React from 'react'

import { ReactComponent as MessageIconSvg } from './assets/message-icon.svg'

const UNBREAKABLE_SPACE = '\u00A0'

const ChoosePreFiltersMessage = () => (
  <div className="br-warning choose-pre-filters">
    <MessageIconSvg aria-hidden />
    <p className="choose-pre-filters-message">
      {`Pour visualiser vos réservations, veuillez sélectionner un ou plusieurs des filtres précédents et cliquer sur «${UNBREAKABLE_SPACE}Afficher${UNBREAKABLE_SPACE}»`}
    </p>
  </div>
)

export default ChoosePreFiltersMessage
