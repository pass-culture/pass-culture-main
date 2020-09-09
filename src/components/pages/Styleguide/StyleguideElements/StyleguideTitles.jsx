import React from 'react'

const StyleguideTitles = () => {
  const title = String.raw`
    <h1>{"Ceci est un titre"}</h1>
  `

  const subtitle = String.raw`
    <h2>{"Ceci est un sous-titre"}</h2>
  `

  return (
    <div>
      <div className="flex-block">
        <h1>
          {'Ceci est un titre'}
        </h1>
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
        <h2>
          {'Ceci est un sous-titre'}
        </h2>
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
