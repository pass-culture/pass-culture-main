/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
//
import ActivationButton from '../layout/buttons/ActivationButton'

const ActivationCard = () => (
  <div
    id="verso-tuto-activation"
    className="flex-rows is-full-height is-white-text text-center"
  >
    <p className="flex-0 text-center is-italic fs20">
      <span className="is-block">Et voilà !</span>
      <span className="is-block">vous pouvez maintenant:</span>
    </p>
    <div className="flex-1 flex-rows flex-center">
      <p>
        <ActivationButton className="pc-theme-gradient px18 pt16 pb18 fs20">
          <span>Activer votre pass Culture</span>
        </ActivationButton>
      </p>
      <p className="fs20 is-italic">
        <span>--</span>
        <span>&nbsp;ou&nbsp;</span>
        <span>--</span>
      </p>
      <p>
        <span className="fs20 is-bold">Explorez les offres</span>
      </p>
    </div>
  </div>
)

export default ActivationCard
