const { extendDefaultPlugins } = require('svgo')

module.exports = {
  plugins: extendDefaultPlugins([
    {
      name: 'addAttributesToSVGElement',
      active: true,
      params: {
        attributes: [{ 'aria-hidden': 'true' }],
      },
    },
    {
      name: 'removeDimensions',
      active: true,
    },
    {
      name: 'removeViewBox',
      active: false,
    },
    {
      name: 'removeXMLNS',
      active: true,
    },
  ]),
}
