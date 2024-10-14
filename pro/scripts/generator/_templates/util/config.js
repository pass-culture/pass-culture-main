export default {
  templateFolderName: 'util',

  filesToGenerate: [
    // 1st file will always be generated
    {
      templateFileName: '<% name %>.ts.mustache',
    },
    // Yes/No questions …
    {
      templateFileName: '<% name %>.spec.ts.mustache',
      question: 'Generate test file?',
      varName: 'spec',
    },
  ],
}
