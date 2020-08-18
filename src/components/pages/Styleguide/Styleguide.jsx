import React from "react"
import Main from '../../layout/Main'
import Titles from '../../layout/Titles/Titles'
import Icon from "../../layout/Icon"

const Styleguide = () => (
  <Main name="styleguide">
    <Titles title="Styleguide" />
    <div>
      <a
        className="primary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <span>
          {'Bouton Primary'}
        </span>
      </a>
    </div>
    <br />
    <div>
      <a
        className="secondary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <span>
          {'Bouton Secondary'}
        </span>
      </a>
    </div>
    <br />
    <div>
    <a
      className="tertiary-button"
      href="/"
      rel="noopener noreferrer"
      target="_blank"
    >
      <Icon svg="ico-external-site-red"/>
      <span>
        {'Bouton Tertiary'}
      </span>
    </a>
    </div>
    <br />
    <div>
      <a
        className="quaternary-button"
        href="/"
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon svg="ico-external-site-red"/>
        <span>
          {'Bouton Quaternary'}
        </span>
      </a>
  </div>
  </Main>
)

export default Styleguide
