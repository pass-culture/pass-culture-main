import ast


def delete_lines(filename, begin_line_number, end_line_number):
    # Create a temporary file name
    temp_filename = filename + ".tmp"

    # Open the input file and the temporary output file
    with open(filename, "r") as file, open(temp_filename, "w") as output:
        for current_line_number, line in enumerate(file, start=1):
            # Write lines to output file if they are not within the delete range
            if current_line_number < begin_line_number or current_line_number > end_line_number:
                output.write(line)

    # Replace the original file with the modified data
    import os

    os.replace(temp_filename, filename)


lines_to_del = None


def remove_route(source_path, route, method, version=None):
    global lines_to_del

    class FunctionRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            global lines_to_del
            for decorator_index, decorator in enumerate(node.decorator_list):
                if (
                    isinstance(decorator, ast.Call)
                    and hasattr(decorator.func, "attr")
                    and decorator.func.attr == "native_route"
                ):
                    route_match = False
                    version_match = version is None  # Assume True if no version specified, handle all versions
                    methods_to_update = False
                    version_explicitly_defined = False
                    method_match = False
                    for keyword in decorator.keywords:
                        if keyword.arg == "methods":
                            method_list = [m.value for m in keyword.value.elts]  # Access elements directly from AST
                            if method in method_list:
                                if len(method_list) > 1:
                                    raise Exception()
                                    # method_list.remove(method)
                                    # keyword.value.elts = [
                                    #     ast.Constant(value=m) for m in method_list
                                    # ]  # Rebuild the AST List
                                    methods_to_update = True
                                else:
                                    method_match = True
                        elif keyword.arg == "version":
                            version_explicitly_defined = True
                            if version and version in ast.literal_eval(keyword.value):
                                version_match = True
                    for arg in decorator.args:
                        if ast.literal_eval(arg) == route:
                            route_match = True
                    # Handle default version 'v1' when not explicitly defined
                    if version == "v1" and not version_explicitly_defined:
                        version_match = True
                    # Check all conditions for retaining the function
                    if route_match and version_match and not methods_to_update and method_match:
                        print("Removing function", node.name)
                        lines_to_del = (
                            min([decorator.lineno for decorator in node.decorator_list]),
                            node.end_lineno,
                        )

                        return node  # Remove function only if no method needs to be updated
            return node

    # Parse the source code into an AST
    tree = ast.parse(source_path)

    # Apply the transformer
    transformed_tree = FunctionRemover().visit(tree)
    print(lines_to_del)
    if lines_to_del:
        delete_lines(source_path, lines_to_del[0], lines_to_del[1])

    # ast.fix_missing_locations(transformed_tree)

    # # Convert the modified AST back to source code using ast.unparse
    # return ast.unparse(transformed_tree)


# Usage: Modify the file paths as needed
source_path = "src/pcapi/routes/native/v1/account.py"


# Specify the method and route
remove_route(source_path, "/profile", "POST", "v1")
