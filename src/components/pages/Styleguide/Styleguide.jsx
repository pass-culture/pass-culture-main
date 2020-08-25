import React from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import StyleguideButtons from './StyleguideButtons'
import StyleguideInputText from './StyleguideInputText'

const Styleguide = () => {
  return (
    <Main name="styleguide">
      <Titles title="Styleguide" />
      <ul>
        <li>
          <a href="#sg-buttons">
            {'Boutons'}
          </a>
        </li>
        <li>
          <a href="#sg-inputtext">
            {'Inputs texte'}
          </a>
        </li>
      </ul>
      <hr className="separator" />
      <h2 id="sg-buttons">
        {'Boutons'}
      </h2>
      <StyleguideButtons />
      <hr className="separator" />
      <h2 id="sg-inputtext">
        {'Inputs'}
      </h2>
      <StyleguideInputText />
    </Main>
  )
}

export default Styleguide
