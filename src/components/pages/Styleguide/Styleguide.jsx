import React from 'react'
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import StyleguideButtons from './StyleguideButtons'
import StyleguideInputText from './StyleguideInputText'

const Styleguide = () => {
  return (
    <Main name="styleguide">
      <Titles title="Styleguide" />
      <h2>
        {'Boutons'}
      </h2>
      <StyleguideButtons />
      <h2>
        {'Inputs'}
      </h2>
      <StyleguideInputText />
    </Main>
  )
}

export default Styleguide
