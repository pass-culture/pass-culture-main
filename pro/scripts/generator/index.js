import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import Mustache from 'mustache'
import {
  createDirectory,
  exitWithScriptError,
  getAnswers,
  getConfig,
  getConfirm,
  makeFilesTree,
  parseAndGenerateFile,
} from './functions.js'

Mustache.tags = ['<%', '%>']

const PRO_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '../../'
)

const TEMPLATES_PATH = path.join(
  path.dirname(fileURLToPath(import.meta.url)),
  '_templates'
)

const ARGV = process.argv
  .slice(2)
  .map((arg) => (arg.startsWith('--') ? arg.slice(2) : arg))

// get template name and element name
const template = ARGV[0]
const name = ARGV[1]

if (!template || !name) {
  exitWithScriptError('Missing arguments (required 2)')
}

// -------------
// Script starts
// -------------

try {
  // Get list of available templates in /_templates/ folder
  const templatesList = await fs.readdir(TEMPLATES_PATH)

  if (!templatesList.includes(template)) {
    exitWithScriptError(`Unknown template: ${template}`)
  }

  // Loads config file for the selected template
  const templatePath = path.join(TEMPLATES_PATH, template)
  const config = await getConfig(templatePath)

  // Asks for user input
  const answers = await getAnswers(config.filesToGenerate, name)

  // Prepares data for mustache template
  const templateData = {
    name,
    ...Object.fromEntries(
      Object.entries(answers)
        .filter(([key]) => key !== 'targetDirectory')
        .map(([key, value]) => [
          key,
          { yes: value === 'Yes', no: value === 'No' },
        ])
    ),
  }

  // Computes final target directory that will contain the generated files
  const targetDirectory = path.join(
    PRO_PATH,
    answers.targetDirectory,
    answers.createNewDirectory ? name : ''
  )

  // Computes a list of files to generate, depending on what the user selected at previous step
  const confirmedFilesToGenerate = config.filesToGenerate
    .filter(
      (file, index) =>
        index === 0 ||
        (answers[file.varName] === 'Yes' && !!file.templateFileName)
    )
    .map((file) => ({
      templateFileName: path.join(templatePath, file.templateFileName),
      renderedFileName: path.join(
        targetDirectory,
        Mustache.render(file.templateFileName.replace('.mustache', ''), {
          name,
        })
      ),
      data: templateData,
    }))

  // Presents a tree of files that are going to be generated …
  console.log('\nThis will generate all these files:\n')
  console.log(
    makeFilesTree({
      baseRoot: path.join(PRO_PATH, answers.targetDirectory),
      newDirectoryName: answers.createNewDirectory ? name : null,
      fileNames: confirmedFilesToGenerate.map(({ renderedFileName }) =>
        path.basename(renderedFileName)
      ),
    }),
    '\n'
  )

  // … and asks for confirmation before creating files
  const confirm = await getConfirm()

  if (!confirm.ok) {
    exitWithScriptError('Cancelled')
  }

  // Creates directory for the new template files if user selected it
  if (answers.createNewDirectory) {
    await createDirectory(targetDirectory)
  }

  // Generate files
  await Promise.all(confirmedFilesToGenerate.map(parseAndGenerateFile))

  // Present report of generated files
  console.log('\n✅ Successfully generated files:\n')
  console.log(
    confirmedFilesToGenerate
      .map(({ renderedFileName }) => ` - ${renderedFileName}`)
      .join('\n'),
    '\n'
  )
} catch (err) {
  exitWithScriptError(err.message)
}
