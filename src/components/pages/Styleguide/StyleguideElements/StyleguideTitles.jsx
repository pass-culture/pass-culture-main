import React from 'react'
import Title from '../../../layout/Titles/Title'
import Subtitle from '../../../layout/Titles/Subtitle'

const StyleguideTitles = () => {
  const title = String.raw`
    <Title
      title="Ceci est un titre"
    />
  `

  const subtitle = String.raw`
    <Subtitle
      subtitle="Ceci est un sous-titre"
    />
  `

  return (
    <div>
      <div className="flex-block">
        <Title title="Ceci est un titre" />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {title}
            </code>
          </pre>
        </div>
      </div>
      <br />

      <div className="flex-block">
        <Subtitle subtitle="Ceci est un sous-titre" />
        <div className="it-description">
          <pre className="it-icon-snippet">
            <code>
              {subtitle}
            </code>
          </pre>
        </div>
      </div>
    </div>
  )
}

export default StyleguideTitles
