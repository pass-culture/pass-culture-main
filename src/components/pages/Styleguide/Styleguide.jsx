import React from 'react'

import Main from 'components/layout/Main'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

import StyleguideAgenda from './StyleguideAgenda'
import StyleguideBanners from './StyleguideElements/StyleguideBanners'
import StyleguideButtons from './StyleguideElements/StyleguideButtons'
import StyleguideCheckboxes from './StyleguideElements/StyleguideCheckboxes'
import StyleguideInputText from './StyleguideElements/StyleguideInputText'
import StyleguideInputTime from './StyleguideElements/StyleguideInputTime'
import StyleguideSelect from './StyleguideElements/StyleguideSelect'
import StyleguideTitles from './StyleguideElements/StyleguideTitles'
import StyleguideTitle from './StyleguideTitles'

const Styleguide = () => (
  <Main name="styleguide">
    <PageTitle title="Guide des styles" />
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
      className="sg-inputtime"
      componentName="InputTime"
    />
    <StyleguideInputTime />

    <StyleguideTitle
      className="sg-select"
      componentName="Select"
    />
    <StyleguideSelect />

    <StyleguideTitle
      className="sg-checkbox"
      componentName="InputCheckbox"
    />
    <StyleguideCheckboxes />

    <StyleguideTitle
      className="sg-banner"
      componentName="Bannière"
    />
    <StyleguideBanners />
  </Main>
)

export default Styleguide
