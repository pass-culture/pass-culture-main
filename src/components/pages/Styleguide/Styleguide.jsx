import React from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import Icon from '../../layout/Icon'

const Styleguide = () => (
  <Main name="styleguide">
    <Titles title="Styleguide" />
    <h2>
      {'Boutons'}
    </h2>
    <div className="flex-block">
      <a
        className="primary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Bouton Primary'}
      </a>
      <div>
        {'Classname'}
        <span className="class-name">
          {' .primary-button'}
        </span>
        {' à utiliser sur balise lien ou bouton'}
      </div>
    </div>
    <hr />
    <div className="flex-block">
      <a
        className="secondary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        {'Bouton Secondary'}
      </a>
      <div>
        {'Classname'}
        <span className="class-name">
          {' .secondary-button'}
        </span>
        {' à utiliser sur balise lien ou bouton'}
      </div>
    </div>
    <hr />
    <div className="flex-block">
      <a
        className="tertiary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site-red" />
        <span>
          {'Bouton Tertiary'}
        </span>
      </a>
      <div>
        {'Classname'}
        <span className="class-name">
          {' .tertiary-button'}
        </span>
        {' à utiliser sur balise lien ou bouton'}
      </div>
    </div>
    <hr />
    <div className="flex-block">
      <a
        className="quaternary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site-red" />
        <span>
          {'Bouton Quaternary'}
        </span>
      </a>
      <div>
        {'Classname'}
        <span className="class-name">
          {' .quaternary-button'}
        </span>
        {' à utiliser sur balise lien ou bouton'}
      </div>
    </div>
    <br />
    <h2>
      {'Inputs'}
    </h2>
    <div className="flex-block">
      <div>
        <label>
          {'Intitulé'}
          <span className="sub-label-input-text">
            {'Intitulé secondaire'}
          </span>
          <input
            className="input-text"
            name="toto"
            placeholder="placeholder"
            type="text"
          />
        </label>
        <label>
          {'Intitulé'}
          <span className="sub-label-input-text">
            {'Intitulé secondaire'}
          </span>
          <input
            className="input-text"
            disabled
            name="toto"
            placeholder="placeholder disabled"
            type="text"
          />
        </label>
      </div>
      <div className="input-text-description">
        {'Classname'}
        <span className="class-name">
          {' .input-text'}
        </span>
        {' à utiliser sur input de type text avec label + sub-label en span si besoin'}
      </div>
    </div>
  </Main>
)

export default Styleguide
