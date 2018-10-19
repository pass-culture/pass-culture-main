/* eslint
  import/no-extraneous-dependencies: 0 */
import path from 'path'
import fse from 'fs-extra'
import parseArgs from 'minimist'
import resemble from 'resemblejs'

// chargement de la configuration des pages a tester
import { pages } from '../../testcafe/visuals.json'
import { ROOT_PATH } from '../../src/utils/config'

// const imageDiff = require('image-diff')

// check si on doit regénéré les images de base
// `testcafe [...options] --force`
const args = parseArgs(process.argv.slice(2))
const useForce = args.force !== undefined

// const diffExt = '-diff.png'
const DEFAULT_TRESHOLD = 0
const baseExt = '-base.png'
const actualExt = '-actual.png'
const outputPath = path.join(__dirname, '..', '..', 'testcafe', 'screenshots')

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// async function generateDiff(title, basepath, actualpath) {
// const options = {
//   ignore: 'antialiasing',
//   output: {
//     errorColor: {
//       blue: 255,
//       green: 0,
//       red: 255,
//     },
//     errorType: 'movement',
//     largeImageThreshold: 1200,
//     outputDiff: true,
//     transparency: 0.3,
//     useCrossOrigin: false,
//   },
//   scaleToSameSize: true,
// }
//
//   const data = await resemble.compareImages(
//     await fse.readFile(basepath),
//     await fse.readFile(actualpath),
//     options
//   )
//
//   const diffpath = path.join(outputPath, `${title}${diffExt}`)
//   await fse.writeFile(diffpath, data.getBuffer())
// }

async function compare(title, treshold = DEFAULT_TRESHOLD) {
  // FIXME -> use promise.then/catch/finally
  const promise = new Promise((resolve, reject) => {
    const basepath = path.join(outputPath, `${title}${baseExt}`)
    const actualpath = path.join(outputPath, `${title}${actualExt}`)
    resemble(basepath)
      .compareTo(actualpath)
      .onComplete(async ({ misMatchPercentage, rawMisMatchPercentage }) => {
        const reason = `${title} images are different`
        const humanPercent = misMatchPercentage
        const imagesAreSame = rawMisMatchPercentage <= treshold
        if (!imagesAreSame) {
          // await generateDiff(title, basepath, actualpath)
          const err = new Error(`${reason} by ${humanPercent}%`)
          return reject(err)
        }
        return resolve()
      })
  })
  return promise
}

pages.forEach(({ delay, title, treshold, url }) => {
  const pageurl = `${ROOT_PATH}${url}`
  fixture('Visual Regression Test').page(pageurl)
  test(title, async t => {
    if (delay) await sleep(delay)
    const baseName = `${title}${baseExt}`
    // check si le fichier base existe
    const basePath = path.join(outputPath, baseName)
    const baseExists = await fse.pathExists(basePath)
    // creation de l'image de base si elle n'existe pas
    if (!baseExists || useForce) await t.takeScreenshot(baseName)
    // compare l'image de base avec l'actuelle
    const actualName = `${title}${actualExt}`
    await t.takeScreenshot(actualName)
    const reason = await compare(title, treshold)
    if (reason) throw new Error(reason)
  })
})
