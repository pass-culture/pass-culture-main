/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

const jaugeHeight = 34
const jaugePadding = 12
const jaugesStyles = {
  container: { height: 'auto', padding: '0' },
  digital: {
    height: `${jaugeHeight}px`,
    top: `${jaugePadding + jaugeHeight + jaugePadding}px`,
  },
  overall: {
    height: `${jaugePadding + (jaugeHeight + jaugePadding) * 2}px`,
  },
  physical: { height: `${jaugeHeight}px`, top: `${jaugePadding}px` },
}

const getPercent = (expense, scale) => {
  const { actual, max } = expense
  const percent = Math.round((actual * 100) / max)
  return percent * scale
}

const MonPassCulture = ({ provider }) => {
  const { expenses } = provider
  expenses.all.actual = 500
  let scale = 1
  const percentOverall = getPercent(expenses.all, scale)
  //
  expenses.physical.actual = expenses.physical.max // 100%
  scale = expenses.physical.max / expenses.all.max
  const percentPhysical = getPercent(expenses.physical, scale)
  //
  expenses.digital.actual = expenses.digital.max
  scale = expenses.digital.max / expenses.all.max
  const percentDigital = getPercent(expenses.digital, scale)
  return (
    <div id="mon-pass-culuture">
      <h3 className="dotted-bottom-primary is-primary-text is-uppercase pb8 px12">
        <i>Mon PassCulture</i>
      </h3>
      <div id="wallet-jauges" className="jauges padded mb40">
        <div className="text overall flex-1">
          <b className="is-block">Il reste {expenses.all.actual} €</b>
          <span className="is-block">sur vore Pass Culture</span>
        </div>
        <div className="flex-columns flex-center mt12">
          <div className="text-containers text-right flex-0 py12 mr8">
            <div className="text physical fs14">
              <span className="is-block">
                jusqu&apos;à <b>{expenses.physical.actual} €</b>
              </span>
              <span className="is-block">pour les biens culturels</span>
            </div>
            <div className="text digital mt8">
              <span className="is-block">
                jusqu&apos;à <b>{expenses.digital.actual} €</b>
              </span>
              <span className="is-block">pour les offres numériques</span>
            </div>
          </div>
          <div
            className="jauges-container flex-1"
            style={{ ...jaugesStyles.container }}
          >
            <div
              className="jauge overall"
              style={{ ...jaugesStyles.overall, width: `${percentOverall}%` }}
            />
            <div
              className="jauge digital"
              style={{ ...jaugesStyles.digital, width: `${percentDigital}%` }}
            />
            <div
              className="jauge physical"
              style={{ ...jaugesStyles.physical, width: `${percentPhysical}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
MonPassCulture.defaultProps = {}
MonPassCulture.propTypes = {
  provider: PropTypes.object.isRequired,
}
export default MonPassCulture
