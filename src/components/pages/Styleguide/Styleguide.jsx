import React from 'react'

import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import StyleguideButtons from './StyleguideElements/StyleguideButtons'
import StyleguideInputText from './StyleguideElements/StyleguideInputText'
import StyleguideAgenda from './StyleguideAgenda'
import StyleguideTitle from './StyleguideTitles'
import StyleguideTitles from './StyleguideElements/StyleguideTitles'
import StyleguideSelect from './StyleguideElements/StyleguideSelect'

const Styleguide = () => (
  <Main name="styleguide">
    <Titles title="Styleguide" />
    <StyleguideAgenda />

    <StyleguideTitle
      className="sg-titles"
      componentName="Titres"
    />
    <StyleguideTitles />

    <StyleguideTitle
      className="sg-buttons"
      componentName="Boutons"
    />
    <StyleguideButtons />

    <StyleguideTitle
      className="sg-inputtext"
      componentName="Inputs"
    />
    <StyleguideInputText />

    <StyleguideTitle
      className="sg-select"
      componentName="Select"
    />
    <StyleguideSelect />
  </Main>
)

export default Styleguide
