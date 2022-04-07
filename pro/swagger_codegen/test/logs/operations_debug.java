class Operation {
    tags: []
    summary: get_bookings_pro <GET>
    description:
    externalDocs: null
    operationId: getBookingsGetBookingsPro
    parameters: [
      class QueryParameter {
        class Parameter {
            name: bookingStatusFilter
            in: null
            description:
            required: false
            deprecated: null
            allowEmptyValue: null
            style: form
            explode: true
            allowReserved: null
            schema: class Schema {
                type: null
                format: null
                $ref: #/components/schemas/bookingStatusFilter
                description: null
                title: null
                multipleOf: null
                maximum: null
                exclusiveMaximum: null
                minimum: null
                exclusiveMinimum: null
                maxLength: null
                minLength: null
                pattern: null
                maxItems: null
                minItems: null
                uniqueItems: null
                maxProperties: null
                minProperties: null
                required: null
                not: null
                properties: null
                additionalProperties: null
                nullable: null
                readOnly: null
                writeOnly: null
                example: null
                externalDocs: null
                deprecated: null
                discriminator: null
                xml: null
            }
            examples: null
            example: null
            content: null
            $ref: null
        }
        in: query
      }, class QueryParameter {
        class Parameter {
            name: awesomeProp
            in: null
            description:
            required: true
            deprecated: null
            allowEmptyValue: null
            style: form
            explode: true
            allowReserved: null
            schema: class Schema {
                type: null
                format: null
                $ref: #/components/schemas/AwesomEnum
                description: null
                title: null
                multipleOf: null
                maximum: null
                exclusiveMaximum: null
                minimum: null
                exclusiveMinimum: null
                maxLength: null
                minLength: null
                pattern: null
                maxItems: null
                minItems: null
                uniqueItems: null
                maxProperties: null
                minProperties: null
                required: null
                not: null
                properties: null
                additionalProperties: null
                nullable: null
                readOnly: null
                writeOnly: null
                example: null
                externalDocs: null
                deprecated: null
                discriminator: null
                xml: null
            }
            examples: null
            example: null
            content: null
            $ref: null
        }
        in: query
      }, class QueryParameter {
        class Parameter {
            name: awesomePropOptional
            in: null
            description:
            required: false
            deprecated: null
            allowEmptyValue: null
            style: form
            explode: true
            allowReserved: null
            schema: class Schema {
                type: null
                format: null
                $ref: #/components/schemas/awesomePropOptional
                description: null
                title: null
                multipleOf: null
                maximum: null
                exclusiveMaximum: null
                minimum: null
                exclusiveMinimum: null
                maxLength: null
                minLength: null
                pattern: null
                maxItems: null
                minItems: null
                uniqueItems: null
                maxProperties: null
                minProperties: null
                required: null
                not: null
                properties: null
                additionalProperties: null
                nullable: null
                readOnly: null
                writeOnly: null
                example: null
                externalDocs: null
                deprecated: null
                discriminator: null
                xml: null
            }
            examples: null
            example: null
            content: null
            $ref: null
        }
        in: query
      }, class QueryParameter {
        class Parameter {
            name: awesomePropUnion
            in: null
            description:
            required: true
            deprecated: null
            allowEmptyValue: null
            style: form
            explode: true
            allowReserved: null
            schema: class Schema {
                type: null
                format: null
                $ref: #/components/schemas/Awesomepropunion
                description: null
                title: null
                multipleOf: null
                maximum: null
                exclusiveMaximum: null
                minimum: null
                exclusiveMinimum: null
                maxLength: null
                minLength: null
                pattern: null
                maxItems: null
                minItems: null
                uniqueItems: null
                maxProperties: null
                minProperties: null
                required: null
                not: null
                properties: null
                additionalProperties: null
                nullable: null
                readOnly: null
                writeOnly: null
                example: null
                externalDocs: null
                deprecated: null
                discriminator: null
                xml: null
            }
            examples: null
            example: null
            content: null
            $ref: null
        }
        in: query
      }, class QueryParameter {
        class Parameter {
            name: awesomePropOptionalUnion
            in: null
            description:
            required: false
            deprecated: null
            allowEmptyValue: null
            style: form
            explode: true
            allowReserved: null
            schema: class Schema {
                type: null
                format: null
                $ref: #/components/schemas/Awesomepropoptionalunion
                description: null
                title: null
                multipleOf: null
                maximum: null
                exclusiveMaximum: null
                minimum: null
                exclusiveMinimum: null
                maxLength: null
                minLength: null
                pattern: null
                maxItems: null
                minItems: null
                uniqueItems: null
                maxProperties: null
                minProperties: null
                required: null
                not: null
                properties: null
                additionalProperties: null
                nullable: null
                readOnly: null
                writeOnly: null
                example: null
                externalDocs: null
                deprecated: null
                discriminator: null
                xml: null
            }
            examples: null
            example: null
            content: null
            $ref: null
        }
        in: query
    }]
    requestBody: null
    responses: class ApiResponses {
      {
        200=class ApiResponse {
            description: OK
            headers: null
            content: class Content {
                {application/json=class MediaType {
                    schema: class Schema {
                        type: null
                        format: null
                        $ref: #/components/schemas/ListBookingsResponseModel
                        description: null
                        title: null
                        multipleOf: null
                        maximum: null
                        exclusiveMaximum: null
                        minimum: null
                        exclusiveMinimum: null
                        maxLength: null
                        minLength: null
                        pattern: null
                        maxItems: null
                        minItems: null
                        uniqueItems: null
                        maxProperties: null
                        minProperties: null
                        required: null
                        not: null
                        properties: null
                        additionalProperties: null
                        nullable: null
                        readOnly: null
                        writeOnly: null
                        example: null
                        externalDocs: null
                        deprecated: null
                        discriminator: null
                        xml: null
                    }
                    examples: null
                    example: null
                    encoding: null
                }}
            }
            links: null
            extensions: null
            $ref: null
        },
        403=class ApiResponse {
            description: Forbidden
            headers: null
            content: null
            links: null
            extensions: null
            $ref: null
        },
        422=class ApiResponse {
            description: Unprocessable Entity
            headers: null
            content: class Content {
                {application/json=class MediaType {
                    schema: class Schema {
                        type: null
                        format: null
                        $ref: #/components/schemas/ValidationError
                        description: null
                        title: null
                        multipleOf: null
                        maximum: null
                        exclusiveMaximum: null
                        minimum: null
                        exclusiveMinimum: null
                        maxLength: null
                        minLength: null
                        pattern: null
                        maxItems: null
                        minItems: null
                        uniqueItems: null
                        maxProperties: null
                        minProperties: null
                        required: null
                        not: null
                        properties: null
                        additionalProperties: null
                        nullable: null
                        readOnly: null
                        writeOnly: null
                        example: null
                        externalDocs: null
                        deprecated: null
                        discriminator: null
                        xml: null
                    }
                    examples: null
                    example: null
                    encoding: null
                }}
            }
            links: null
            extensions: null
            $ref: null
        }
      }
      extensions: null
    }
    callbacks: null
    deprecated: null
    security: null
    servers: null
}

// 14:46:15.790 [Thread-1] INFO  i.s.codegen.v3.DefaultGenerator - ############ Operation info ############
[ {
  "importPath" : ".Default",
  "appVersion" : "1",
  "generatedYear" : "2022",
  "generatorClass" : "io.swagger.codegen.v3.generators.typescript.TypeScriptFetchClientCodegen",
  "modelPackage" : "",
  "sortParamsByRequiredFlag" : true,
  "templateDir" : "/local/swagger_codegen/gen_templates",
  "classVarName" : "default",
  "hasModel" : true,
  "generateModelDocs" : true,
  "hasImport" : true,
  "generateModelTests" : true,
  "basePathWithoutHost" : "",
  "generateApiTests" : true,
  "classFilename" : "DefaultApi",
  "operations" : {
    "classname" : "DefaultApi",
    "operation" : [ {
      "vendorExtensions" : {
        "x-has-consumes" : false,
        "x-has-required-params" : true,
        "x-is-restful-show" : false,
        "x-is-get-method" : true,
        "x-has-reference" : true,
        "x-is-restful-index" : false,
        "x-is-restful-destroy" : false,
        "x-has-more" : false,
        "x-has-params" : true,
        "x-has-optional-params" : true,
        "x-is-restful" : false,
        "x-is-restful-update" : false,
        "x-has-produces" : true,
        "x-is-restful-create" : false
      },
      "responseHeaders" : [ ],
      "returnTypeIsPrimitive" : false,
      "returnSimpleType" : true,
      "subresourceOperation" : false,
      "path" : "/bookings/pro",
      "operationId" : "getBookingsGetBookingsPro",
      "returnType" : "ListBookingsResponseModel",
      "httpMethod" : "GET",
      "returnBaseType" : "ListBookingsResponseModel",
      "summary" : "get_bookings_pro <GET>",
      "unescapedNotes" : "",
      "notes" : "",
      "baseName" : "Default",
      "defaultResponse" : "undefined",
      "testPath" : "/bookings/pro",
      "produces" : [ {
        "mediaType" : "application/json"
      } ],
      "contents" : [ {
        "parameters" : [ {
          "vendorExtensions" : {
            "x-is-nullable" : false,
            "x-is-primitive-type" : false,
            "x-is-query-param" : true,
            "x-has-more" : true
          },
          "secondaryParam" : false,
          "baseName" : "awesomeProp",
          "paramName" : "awesomeProp",
          "dataType" : "AwesomEnum",
          "description" : "",
          "unescapedDescription" : "",
          "jsonSchema" : "{\n  \"name\" : \"awesomeProp\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/AwesomEnum\"\n  }\n}",
          "nullable" : false,
          "required" : true,
          "exclusiveMaximum" : false,
          "exclusiveMinimum" : false,
          "uniqueItems" : false,
          "isBodyParam" : false,
          "isCookieParam" : false,
          "isQueryParam" : true,
          "isFormParam" : false,
          "isPathParam" : false,
          "isHeaderParam" : false,
          "notFile" : true,
          "isContainer" : false,
          "isPrimitiveType" : false,
          "isEnum" : false,
          "isListContainer" : false,
          "isMapContainer" : false,
          "isAlias" : false,
          "isInteger" : false,
          "isNumber" : false,
          "hasHeaders" : false,
          "isString" : false,
          "isNumeric" : false,
          "isLong" : false,
          "isFloat" : false,
          "isDouble" : false,
          "isByteArray" : false,
          "isBoolean" : false,
          "isDate" : false,
          "isDateTime" : false,
          "isUuid" : false,
          "isDefault" : false,
          "isMultipart" : false,
          "isResponseBinary" : false,
          "isResponseFile" : false,
          "isBinary" : false,
          "isFile" : false,
          "isArrayModel" : false,
          "isObject" : false,
          "hasInnerObject" : false,
          "isNotContainer" : false,
          "isReadOnly" : false,
          "isNullable" : false,
          "isCollectionFormatMulti" : false,
          "hasMore" : true
        }, {
          "vendorExtensions" : {
            "x-is-nullable" : false,
            "x-is-object" : true,
            "x-is-primitive-type" : false,
            "x-is-query-param" : true,
            "x-has-more" : true
          },
          "secondaryParam" : true,
          "baseName" : "awesomePropUnion",
          "paramName" : "awesomePropUnion",
          "dataType" : "Awesomepropunion",
          "description" : "",
          "unescapedDescription" : "",
          "jsonSchema" : "{\n  \"name\" : \"awesomePropUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropunion\"\n  }\n}",
          "nullable" : false,
          "required" : true,
          "exclusiveMaximum" : false,
          "exclusiveMinimum" : false,
          "uniqueItems" : false,
          "isBodyParam" : false,
          "isCookieParam" : false,
          "isQueryParam" : true,
          "isFormParam" : false,
          "isPathParam" : false,
          "isHeaderParam" : false,
          "notFile" : true,
          "isContainer" : false,
          "isPrimitiveType" : false,
          "isEnum" : false,
          "isListContainer" : false,
          "isMapContainer" : false,
          "isAlias" : false,
          "isInteger" : false,
          "isNumber" : false,
          "hasHeaders" : false,
          "isString" : false,
          "isNumeric" : false,
          "isLong" : false,
          "isFloat" : false,
          "isDouble" : false,
          "isByteArray" : false,
          "isBoolean" : false,
          "isDate" : false,
          "isDateTime" : false,
          "isUuid" : false,
          "isDefault" : false,
          "isMultipart" : false,
          "isResponseBinary" : false,
          "isResponseFile" : false,
          "isBinary" : false,
          "isFile" : false,
          "isArrayModel" : false,
          "isObject" : true,
          "hasInnerObject" : false,
          "isNotContainer" : false,
          "isReadOnly" : false,
          "isNullable" : false,
          "isCollectionFormatMulti" : false,
          "hasMore" : true
        }, {
          "vendorExtensions" : {
            "x-is-nullable" : false,
            "x-is-object" : true,
            "x-is-primitive-type" : false,
            "x-is-query-param" : true,
            "x-has-more" : true
          },
          "secondaryParam" : true,
          "baseName" : "bookingStatusFilter",
          "paramName" : "bookingStatusFilter",
          "dataType" : "BookingStatusFilter",
          "description" : "",
          "unescapedDescription" : "",
          "jsonSchema" : "{\n  \"name\" : \"bookingStatusFilter\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/bookingStatusFilter\"\n  }\n}",
          "nullable" : false,
          "required" : false,
          "exclusiveMaximum" : false,
          "exclusiveMinimum" : false,
          "uniqueItems" : false,
          "isBodyParam" : false,
          "isCookieParam" : false,
          "isQueryParam" : true,
          "isFormParam" : false,
          "isPathParam" : false,
          "isHeaderParam" : false,
          "notFile" : true,
          "isContainer" : false,
          "isPrimitiveType" : false,
          "isEnum" : false,
          "isListContainer" : false,
          "isMapContainer" : false,
          "isAlias" : false,
          "isInteger" : false,
          "isNumber" : false,
          "hasHeaders" : false,
          "isString" : false,
          "isNumeric" : false,
          "isLong" : false,
          "isFloat" : false,
          "isDouble" : false,
          "isByteArray" : false,
          "isBoolean" : false,
          "isDate" : false,
          "isDateTime" : false,
          "isUuid" : false,
          "isDefault" : false,
          "isMultipart" : false,
          "isResponseBinary" : false,
          "isResponseFile" : false,
          "isBinary" : false,
          "isFile" : false,
          "isArrayModel" : false,
          "isObject" : true,
          "hasInnerObject" : false,
          "isNotContainer" : false,
          "isReadOnly" : false,
          "isNullable" : false,
          "isCollectionFormatMulti" : false,
          "hasMore" : true
        }, {
          "vendorExtensions" : {
            "x-is-nullable" : false,
            "x-is-object" : true,
            "x-is-primitive-type" : false,
            "x-is-query-param" : true,
            "x-has-more" : true
          },
          "secondaryParam" : true,
          "baseName" : "awesomePropOptional",
          "paramName" : "awesomePropOptional",
          "dataType" : "AwesomePropOptional",
          "description" : "",
          "unescapedDescription" : "",
          "jsonSchema" : "{\n  \"name\" : \"awesomePropOptional\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/awesomePropOptional\"\n  }\n}",
          "nullable" : false,
          "required" : false,
          "exclusiveMaximum" : false,
          "exclusiveMinimum" : false,
          "uniqueItems" : false,
          "isBodyParam" : false,
          "isCookieParam" : false,
          "isQueryParam" : true,
          "isFormParam" : false,
          "isPathParam" : false,
          "isHeaderParam" : false,
          "notFile" : true,
          "isContainer" : false,
          "isPrimitiveType" : false,
          "isEnum" : false,
          "isListContainer" : false,
          "isMapContainer" : false,
          "isAlias" : false,
          "isInteger" : false,
          "isNumber" : false,
          "hasHeaders" : false,
          "isString" : false,
          "isNumeric" : false,
          "isLong" : false,
          "isFloat" : false,
          "isDouble" : false,
          "isByteArray" : false,
          "isBoolean" : false,
          "isDate" : false,
          "isDateTime" : false,
          "isUuid" : false,
          "isDefault" : false,
          "isMultipart" : false,
          "isResponseBinary" : false,
          "isResponseFile" : false,
          "isBinary" : false,
          "isFile" : false,
          "isArrayModel" : false,
          "isObject" : true,
          "hasInnerObject" : false,
          "isNotContainer" : false,
          "isReadOnly" : false,
          "isNullable" : false,
          "isCollectionFormatMulti" : false,
          "hasMore" : true
        }, {
          "vendorExtensions" : {
            "x-is-nullable" : false,
            "x-is-object" : true,
            "x-is-primitive-type" : false,
            "x-is-query-param" : true,
            "x-has-more" : false
          },
          "secondaryParam" : true,
          "baseName" : "awesomePropOptionalUnion",
          "paramName" : "awesomePropOptionalUnion",
          "dataType" : "Awesomepropoptionalunion",
          "description" : "",
          "unescapedDescription" : "",
          "jsonSchema" : "{\n  \"name\" : \"awesomePropOptionalUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropoptionalunion\"\n  }\n}",
          "nullable" : false,
          "required" : false,
          "exclusiveMaximum" : false,
          "exclusiveMinimum" : false,
          "uniqueItems" : false,
          "isBodyParam" : false,
          "isCookieParam" : false,
          "isQueryParam" : true,
          "isFormParam" : false,
          "isPathParam" : false,
          "isHeaderParam" : false,
          "notFile" : true,
          "isContainer" : false,
          "isPrimitiveType" : false,
          "isEnum" : false,
          "isListContainer" : false,
          "isMapContainer" : false,
          "isAlias" : false,
          "isInteger" : false,
          "isNumber" : false,
          "hasHeaders" : false,
          "isString" : false,
          "isNumeric" : false,
          "isLong" : false,
          "isFloat" : false,
          "isDouble" : false,
          "isByteArray" : false,
          "isBoolean" : false,
          "isDate" : false,
          "isDateTime" : false,
          "isUuid" : false,
          "isDefault" : false,
          "isMultipart" : false,
          "isResponseBinary" : false,
          "isResponseFile" : false,
          "isBinary" : false,
          "isFile" : false,
          "isArrayModel" : false,
          "isObject" : true,
          "hasInnerObject" : false,
          "isNotContainer" : false,
          "isReadOnly" : false,
          "isNullable" : false,
          "isCollectionFormatMulti" : false,
          "hasMore" : false
        } ],
        "contentExtensions" : { },
        "isForm" : false
      } ],
      "allParams" : [ {
        "vendorExtensions" : {
          "x-is-nullable" : false,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true,
          "x-has-more" : true
        },
        "secondaryParam" : false,
        "baseName" : "awesomeProp",
        "paramName" : "awesomeProp",
        "dataType" : "AwesomEnum",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomeProp\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/AwesomEnum\"\n  }\n}",
        "nullable" : false,
        "required" : true,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : false,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true,
          "x-has-more" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropUnion",
        "paramName" : "awesomePropUnion",
        "dataType" : "Awesomepropunion",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropunion\"\n  }\n}",
        "nullable" : false,
        "required" : true,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true,
          "x-has-more" : true
        },
        "secondaryParam" : true,
        "baseName" : "bookingStatusFilter",
        "paramName" : "bookingStatusFilter",
        "dataType" : "BookingStatusFilter",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"bookingStatusFilter\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/bookingStatusFilter\"\n  }\n}",
        "nullable" : false,
        "required" : false,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true,
          "x-has-more" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropOptional",
        "paramName" : "awesomePropOptional",
        "dataType" : "AwesomePropOptional",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropOptional\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/awesomePropOptional\"\n  }\n}",
        "nullable" : false,
        "required" : false,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true,
          "x-has-more" : false
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropOptionalUnion",
        "paramName" : "awesomePropOptionalUnion",
        "dataType" : "Awesomepropoptionalunion",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropOptionalUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropoptionalunion\"\n  }\n}",
        "nullable" : false,
        "required" : false,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : false
      } ],
      "bodyParams" : [ ],
      "pathParams" : [ ],
      "queryParams" : [ {
        "vendorExtensions" : {
          "x-has-more" : true,
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : false,
        "baseName" : "bookingStatusFilter",
        "paramName" : "bookingStatusFilter",
        "dataType" : "BookingStatusFilter",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"bookingStatusFilter\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/bookingStatusFilter\"\n  }\n}",
        "nullable" : false,
        "required" : false,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-has-more" : true,
          "x-is-nullable" : false,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomeProp",
        "paramName" : "awesomeProp",
        "dataType" : "AwesomEnum",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomeProp\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/AwesomEnum\"\n  }\n}",
        "nullable" : false,
        "required" : true,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : false,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-has-more" : true,
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropOptional",
        "paramName" : "awesomePropOptional",
        "dataType" : "AwesomePropOptional",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropOptional\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/awesomePropOptional\"\n  }\n}",
        "nullable" : false,
        "required" : false,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-has-more" : true,
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropUnion",
        "paramName" : "awesomePropUnion",
        "dataType" : "Awesomepropunion",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropunion\"\n  }\n}",
        "nullable" : false,
        "required" : true,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-has-more" : false,
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropOptionalUnion",
        "paramName" : "awesomePropOptionalUnion",
        "dataType" : "Awesomepropoptionalunion",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropOptionalUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : false,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropoptionalunion\"\n  }\n}",
        "nullable" : false,
        "required" : false,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : false
      } ],
      "headerParams" : [ ],
      "cookieParams" : [ ],
      "formParams" : [ ],
      "requiredParams" : [ {
        "vendorExtensions" : {
          "x-has-more" : true,
          "x-is-nullable" : false,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : false,
        "baseName" : "awesomeProp",
        "paramName" : "awesomeProp",
        "dataType" : "AwesomEnum",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomeProp\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/AwesomEnum\"\n  }\n}",
        "nullable" : false,
        "required" : true,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : false,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-has-more" : false,
          "x-is-nullable" : false,
          "x-is-object" : true,
          "x-is-primitive-type" : false,
          "x-is-query-param" : true
        },
        "secondaryParam" : true,
        "baseName" : "awesomePropUnion",
        "paramName" : "awesomePropUnion",
        "dataType" : "Awesomepropunion",
        "description" : "",
        "unescapedDescription" : "",
        "jsonSchema" : "{\n  \"name\" : \"awesomePropUnion\",\n  \"in\" : \"query\",\n  \"description\" : \"\",\n  \"required\" : true,\n  \"style\" : \"form\",\n  \"explode\" : true,\n  \"schema\" : {\n    \"$ref\" : \"#/components/schemas/Awesomepropunion\"\n  }\n}",
        "nullable" : false,
        "required" : true,
        "exclusiveMaximum" : false,
        "exclusiveMinimum" : false,
        "uniqueItems" : false,
        "isBodyParam" : false,
        "isCookieParam" : false,
        "isQueryParam" : true,
        "isFormParam" : false,
        "isPathParam" : false,
        "isHeaderParam" : false,
        "notFile" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : true,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : false
      } ],
      "tags" : [ {
        "name" : "default"
      } ],
      "responses" : [ {
        "vendorExtensions" : {
          "x-has-headers" : false,
          "x-is-primitive-type" : false,
          "x-has-more" : true,
          "x-is-simple-type" : true,
          "x-is-default" : true
        },
        "headers" : [ ],
        "code" : "200",
        "message" : "OK",
        "contents" : [ ],
        "examples" : [ ],
        "dataType" : "ListBookingsResponseModel",
        "baseType" : "ListBookingsResponseModel",
        "schema" : {
          "$ref" : "#/components/schemas/ListBookingsResponseModel"
        },
        "jsonSchema" : "{\n  \"description\" : \"OK\",\n  \"content\" : {\n    \"application/json\" : {\n      \"schema\" : {\n        \"$ref\" : \"#/components/schemas/ListBookingsResponseModel\"\n      }\n    }\n  }\n}",
        "primitiveType" : false,
        "wildcard" : false,
        "simpleType" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : true,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : false,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-is-map-container" : false,
          "x-has-headers" : false,
          "x-is-primitive-type" : true,
          "x-has-more" : true,
          "x-is-simple-type" : true,
          "x-is-default" : false,
          "x-is-list-container" : false
        },
        "headers" : [ ],
        "code" : "403",
        "message" : "Forbidden",
        "contents" : [ ],
        "jsonSchema" : "{\n  \"description\" : \"Forbidden\"\n}",
        "primitiveType" : true,
        "wildcard" : false,
        "simpleType" : true,
        "isContainer" : false,
        "isPrimitiveType" : true,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : false,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : true
      }, {
        "vendorExtensions" : {
          "x-has-headers" : false,
          "x-is-primitive-type" : false,
          "x-has-more" : false,
          "x-is-simple-type" : true,
          "x-is-default" : false
        },
        "headers" : [ ],
        "code" : "422",
        "message" : "Unprocessable Entity",
        "contents" : [ ],
        "examples" : [ ],
        "dataType" : "ValidationError",
        "baseType" : "ValidationError",
        "schema" : {
          "$ref" : "#/components/schemas/ValidationError"
        },
        "jsonSchema" : "{\n  \"description\" : \"Unprocessable Entity\",\n  \"content\" : {\n    \"application/json\" : {\n      \"schema\" : {\n        \"$ref\" : \"#/components/schemas/ValidationError\"\n      }\n    }\n  }\n}",
        "primitiveType" : false,
        "wildcard" : false,
        "simpleType" : true,
        "isContainer" : false,
        "isPrimitiveType" : false,
        "isEnum" : false,
        "isListContainer" : false,
        "isMapContainer" : false,
        "isAlias" : false,
        "isInteger" : false,
        "isNumber" : false,
        "hasHeaders" : false,
        "isString" : false,
        "isNumeric" : false,
        "isLong" : false,
        "isFloat" : false,
        "isDouble" : false,
        "isByteArray" : false,
        "isBoolean" : false,
        "isDate" : false,
        "isDateTime" : false,
        "isUuid" : false,
        "isDefault" : false,
        "isMultipart" : false,
        "isResponseBinary" : false,
        "isResponseFile" : false,
        "isBinary" : false,
        "isFile" : false,
        "isArrayModel" : false,
        "isObject" : false,
        "hasInnerObject" : false,
        "isNotContainer" : false,
        "isReadOnly" : false,
        "isNullable" : false,
        "isCollectionFormatMulti" : false,
        "hasMore" : false
      } ],
      "imports" : [ "BookingStatusFilter", "AwesomEnum", "ListBookingsResponseModel", "Awesomepropunion", "ValidationError", "AwesomePropOptional", "Awesomepropoptionalunion" ],
      "examples" : [ {
        "contentType" : "application/json",
        "example" : "{\n  \"total\" : 0\n}"
      } ],
      "nickname" : "getBookingsGetBookingsPro",
      "operationIdLowerCase" : "getbookingsgetbookingspro",
      "operationIdCamelCase" : "GetBookingsGetBookingsPro",
      "operationIdSnakeCase" : "get_bookings_get_bookings_pro",
      "hasBodyParam" : false,
      "isRestfulShow" : false,
      "isRestfulIndex" : false,
      "isRestfulCreate" : false,
      "isRestfulUpdate" : false,
      "isRestfulDestroy" : false,
      "isRestful" : false,
      "hasQueryParams" : true,
      "hasHeaderParams" : false,
      "hasCookieParams" : false,
      "hasPathParams" : false,
      "hasFormParams" : false,
      "hasExamples" : true,
      "isBodyAllowed" : false,
      "isDeprecated" : false,
      "hasAuthMethods" : false,
      "hasConsumes" : false,
      "hasProduces" : true,
      "hasParams" : true,
      "hasOptionalParams" : true,
      "hasRequiredParams" : true,
      "hasReference" : true,
      "isContainer" : false,
      "isPrimitiveType" : false,
      "isEnum" : false,
      "isListContainer" : false,
      "isMapContainer" : false,
      "isAlias" : false,
      "isInteger" : false,
      "isNumber" : false,
      "hasHeaders" : false,
      "isString" : false,
      "isNumeric" : false,
      "isLong" : false,
      "isFloat" : false,
      "isDouble" : false,
      "isByteArray" : false,
      "isBoolean" : false,
      "isDate" : false,
      "isDateTime" : false,
      "isUuid" : false,
      "isDefault" : false,
      "isMultipart" : false,
      "isResponseBinary" : false,
      "isResponseFile" : false,
      "isBinary" : false,
      "isFile" : false,
      "isArrayModel" : false,
      "isObject" : false,
      "hasInnerObject" : false,
      "isNotContainer" : false,
      "isReadOnly" : false,
      "isNullable" : false,
      "isCollectionFormatMulti" : false,
      "hasMore" : false
    } ],
    "pathPrefix" : "default"
  },
  "inputSpec" : "{\n  \"components\": {\n    \"schemas\": {\n      \"AwesomEnum\": {\n        \"description\": \"An enumeration.\",\n        \"enum\": [\n          \"hello\",\n          \"good by\"\n        ],\n        \"title\": \"AwesomEnum\"\n      },\n      \"BookingStatusFilter\": {\n        \"description\": \"An enumeration.\",\n        \"enum\": [\n          \"booked\",\n          \"validated\",\n          \"reimbursed\"\n        ],\n        \"title\": \"BookingStatusFilter\"\n      },\n      \"ListBookingsQueryModel\": {\n        \"properties\": {\n          \"awesomeProp\": {\n            \"$ref\": \"#/components/schemas/AwesomEnum\"\n          },\n          \"awesomePropOptional\": {\n            \"anyOf\": [\n              {\n                \"title\": \"AwesomEnum\",\n                \"$ref\": \"#/components/schemas/AwesomEnum\",\n                \"type\": \"string\"\n              }\n            ],\n            \"nullable\": true\n          },\n          \"awesomePropOptionalUnion\": {\n            \"anyOf\": [\n              {\n                \"title\": \"AwesomEnum\",\n                \"$ref\": \"#/components/schemas/AwesomEnum\",\n                \"type\": \"string\"\n              },\n              {\n                \"type\": \"integer\"\n              }\n            ],\n            \"nullable\": true,\n            \"title\": \"Awesomepropoptionalunion\"\n          },\n          \"awesomePropUnion\": {\n            \"anyOf\": [\n              {\n                \"title\": \"AwesomEnum\",\n                \"$ref\": \"#/components/schemas/AwesomEnum\",\n                \"type\": \"string\"\n              },\n              {\n                \"type\": \"integer\"\n              }\n            ],\n            \"title\": \"Awesomepropunion\"\n          },\n          \"bookingStatusFilter\": {\n            \"anyOf\": [\n              {\n                \"$ref\": \"#/components/schemas/BookingStatusFilter\"\n              }\n            ],\n            \"nullable\": true\n          }\n        },\n        \"required\": [\n          \"awesomeProp\",\n          \"awesomePropUnion\"\n        ],\n        \"title\": \"ListBookingsQueryModel\",\n        \"type\": \"object\"\n      },\n      \"ListBookingsResponseModel\": {\n        \"properties\": {\n          \"total\": {\n            \"title\": \"Total\",\n            \"type\": \"integer\"\n          }\n        },\n        \"required\": [\n        ],\n        \"title\": \"ListBookingsResponseModel\",\n        \"type\": \"object\"\n      }\n    },\n    \"ValidationError\": {\n      \"description\": \"Model of a validation error response.\",\n      \"items\": {\n        \"$ref\": \"#/components/schemas/ValidationErrorElement\"\n      },\n      \"title\": \"ValidationError\",\n      \"type\": \"array\"\n    },\n    \"ValidationErrorElement\": {\n      \"description\": \"Model of a validation error response element.\",\n      \"properties\": {\n        \"ctx\": {\n          \"title\": \"Error context\",\n          \"type\": \"object\"\n        },\n        \"loc\": {\n          \"items\": {\n            \"type\": \"string\"\n          },\n          \"title\": \"Missing field name\",\n          \"type\": \"array\"\n        },\n        \"msg\": {\n          \"title\": \"Error message\",\n          \"type\": \"string\"\n        },\n        \"type\": {\n          \"title\": \"Error type\",\n          \"type\": \"string\"\n        }\n      },\n      \"required\": [\n        \"loc\",\n        \"msg\",\n        \"type\"\n      ],\n      \"title\": \"ValidationErrorElement\",\n      \"type\": \"object\"\n    }\n  },\n  \"info\": {\n    \"title\": \"pass Culture pro private API\",\n    \"version\": \"1\"\n  },\n  \"openapi\": \"3.0.3\",\n  \"paths\": {\n    \"/bookings/pro\": {\n      \"get\": {\n        \"description\": \"\",\n        \"operationId\": \"getBookingsGetBookingsPro\",\n        \"parameters\": [\n          {\n            \"description\": \"\",\n            \"in\": \"query\",\n            \"name\": \"bookingStatusFilter\",\n            \"required\": false,\n            \"schema\": {\n              \"anyOf\": [\n                {\n                  \"$ref\": \"#/components/schemas/BookingStatusFilter\"\n                }\n              ],\n              \"nullable\": true\n            }\n          },\n          {\n            \"description\": \"\",\n            \"in\": \"query\",\n            \"name\": \"awesomeProp\",\n            \"required\": true,\n            \"schema\": {\n              \"$ref\": \"#/components/schemas/AwesomEnum\"\n            }\n          },\n          {\n            \"description\": \"\",\n            \"in\": \"query\",\n            \"name\": \"awesomePropOptional\",\n            \"required\": false,\n            \"schema\": {\n              \"anyOf\": [\n                {\n                  \"$ref\": \"#/components/schemas/AwesomEnum\"\n                }\n              ],\n              \"nullable\": true\n            }\n          },\n          {\n            \"description\": \"\",\n            \"in\": \"query\",\n            \"name\": \"awesomePropUnion\",\n            \"required\": true,\n            \"schema\": {\n              \"anyOf\": [\n                {\n                  \"$ref\": \"#/components/schemas/AwesomEnum\"\n                },\n                {\n                  \"type\": \"integer\"\n                }\n              ],\n              \"title\": \"Awesomepropunion\"\n            }\n          },\n          {\n            \"description\": \"\",\n            \"in\": \"query\",\n            \"name\": \"awesomePropOptionalUnion\",\n            \"required\": false,\n            \"schema\": {\n              \"anyOf\": [\n                {\n                  \"$ref\": \"#/components/schemas/AwesomEnum\"\n                },\n                {\n                  \"type\": \"integer\"\n                }\n              ],\n              \"nullable\": true,\n              \"title\": \"Awesomepropoptionalunion\"\n            }\n          }\n        ],\n        \"responses\": {\n          \"200\": {\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"$ref\": \"#/components/schemas/ListBookingsResponseModel\"\n                }\n              }\n            },\n            \"description\": \"OK\"\n          },\n          \"403\": {\n            \"description\": \"Forbidden\"\n          },\n          \"422\": {\n            \"content\": {\n              \"application/json\": {\n                \"schema\": {\n                  \"$ref\": \"#/components/schemas/ValidationError\"\n                }\n              }\n            },\n            \"description\": \"Unprocessable Entity\"\n          }\n        },\n        \"summary\": \"get_bookings_pro <GET>\",\n        \"tags\": []\n      }\n    }\n  },\n  \"security\": [],\n  \"tags\": []\n}",
  "hideGenerationTimestamp" : true,
  "baseName" : "Default",
  "unescapedAppDescription" : "No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)",
  "package" : "",
  "imports" : [ {
    "import" : "AwesomEnum"
  }, {
    "import" : "AwesomePropOptional"
  }, {
    "import" : "Awesomepropoptionalunion"
  }, {
    "import" : "Awesomepropunion"
  }, {
    "import" : "BookingStatusFilter"
  }, {
    "import" : "ListBookingsResponseModel"
  }, {
    "import" : "ValidationError"
  } ],
  "appName" : "pass Culture pro private API",
  "contextPath" : "",
  "appDescription" : "No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)",
  "generateApiDocs" : true,
  "generatorVersion" : "3.0.33",
  "releaseNote" : "Minor update",
  "version" : "1",
  "gitRepoBaseURL" : "https://github.com",
  "basePath" : "/",
  "classname" : "DefaultApi",
  "modelPropertyNaming" : "camelCase",
  "gitRepoId" : "GIT_REPO_ID",
  "generatedDate" : "2022-04-07T14:46:15.664Z[GMT]",
  "templateEngine" : "handlebars",
  "gitUserId" : "GIT_USER_ID"
} ]