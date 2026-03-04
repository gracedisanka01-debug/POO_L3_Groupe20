import ast
import os

SRC = r"c:\Users\pc\Documents\src\housing_model.py"
DOT = r"c:\Users\pc\Documents\housing_model.dot"
PNG = r"c:\Users\pc\Documents\housing_model.png"

with open(SRC, 'r', encoding='utf-8') as f:
    src = f.read()

module = ast.parse(src)

classes = []
for node in module.body:
    if isinstance(node, ast.ClassDef):
        cls = {'name': node.name, 'attrs': [], 'methods': []}
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # collect methods and args
                args = [a.arg for a in item.args.args]
                # remove 'self' from display
                if args and args[0] == 'self':
                    args = args[1:]
                cls['methods'].append((item.name, args))
                # inspect __init__ for self attributes
                if item.name == '__init__':
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    # target.attr is a string
                                    cls['attrs'].append(target.attr)
                        elif isinstance(stmt, ast.AnnAssign):
                            target = stmt.target
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                cls['attrs'].append(target.attr)
        classes.append(cls)

# Fallback: if no attrs found via __init__, try to find attributes assigned at class level
for node in module.body:
    if isinstance(node, ast.ClassDef):
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        # class attribute
                        for cls in classes:
                            if cls['name'] == node.name and target.id not in cls['attrs']:
                                cls['attrs'].append(target.id)

# Build DOT
lines = ["digraph G {", "rankdir=LR;", "node [shape=record, fontsize=10];"]
for cls in classes:
    name = cls['name']
    attrs = '\\l'.join(cls['attrs']) + ('\\l' if cls['attrs'] else '')
    methods = '\\l'.join([m[0] + '(' + ', '.join(m[1]) + ')' for m in cls['methods']]) + ('\\l' if cls['methods'] else '')
    label = "{%(name)s|%(attrs)s|%(methods)s}" % {'name': name, 'attrs': attrs, 'methods': methods}
    lines.append(f'{name} [label="{label}"];')

lines.append('}')

dot_text = '\n'.join(lines)
with open(DOT, 'w', encoding='utf-8') as f:
    f.write(dot_text)

print('Wrote DOT to', DOT)

# Try to render using graphviz Python package
try:
    from graphviz import Source
    s = Source(dot_text)
    s.render(filename=PNG, format='png', cleanup=True)
    print('Rendered PNG to', PNG)
except Exception as e:
    print('Could not render PNG automatically:', e)
    print('You can render with Graphviz: dot -Tpng', DOT, '-o', PNG)
