# 1. Importa la librería pydot. Esta librería es la que nos permite crear y manipular los diagramas de puntos (dots), que es el formato que usa Graphviz para dibujar los gráficos. Es el puente entre Python y Graphviz.
import pydot

# 2. Importa la clase ObjectId del módulo bson.objectid. ObjectId es el tipo de dato especial que usa MongoDB para generar identificadores únicos (_id) para cada documento. Lo necesitamos para simular datos de MongoDB y para identificar campos que podrían ser claves foráneas.
from bson.objectid import ObjectId

# 3. Importa la librería random. Se usará más adelante para generar un número aleatorio para el nombre del archivo de imagen del gráfico, evitando que se sobrescriba si ejecutas el script varias veces.
import random

# 4. Importa la librería traceback. Esta es útil para mostrar información detallada del error si algo falla, especialmente útil para depurar problemas complejos.
import traceback

# 5. Define una función llamada detect_relationships que recibe un argumento: db_data. db_data se espera que sea un diccionario donde las claves son nombres de colecciones y los valores son listas de documentos (diccionarios) de esa colección.
def detect_relationships(db_data):

# 6. Inicializa un conjunto (set) vacío llamado detected_relationships. Usamos un conjunto para guardar las relaciones encontradas porque automáticamente evita duplicados. Cada relación será una tupla.
    detected_relationships = set()

# 7. Obtiene una lista de todos los nombres de las colecciones (las claves del diccionario db_data). Esto será útil para verificar si una posible colección referenciada realmente existe.
    collection_names = list(db_data.keys())

# 8. Imprime un mensaje indicando que comienza el proceso de detección. El \n al principio asegura una línea en blanco antes del mensaje para mejor formato.
    print("\n--- Iniciando detección automática de relaciones ---")

# 9. Inicia un bucle 'for' que itera sobre cada par clave-valor en db_data. En cada iteración, source_collection_name será el nombre de la colección (ej: "posts") y collection_data será la lista de documentos de esa colección.
    for source_collection_name, collection_data in db_data.items():

# 10. Verifica si la lista collection_data está vacía (es decir, si la colección no tiene documentos).
        if not collection_data:

# 11. Si la colección está vacía, imprime un mensaje indicándolo.
            print(f"Colección '{source_collection_name}' está vacía, saltando...")

# 12. Usa 'continue' para saltar el resto del código dentro de este bucle 'for' y pasar a la siguiente colección. No podemos analizar campos si no hay documentos.
            continue

# 13. Si la colección no está vacía, toma el *primer* documento de la lista (índice 0). La lógica asume que la estructura del primer documento es representativa de los demás en esa colección para detectar relaciones.
        first_doc = collection_data[0]

# 14. Imprime un mensaje indicando qué colección se está analizando y muestra los nombres de los campos (claves del diccionario) del primer documento.
        print(f"Analizando campos del primer documento en '{source_collection_name}': {list(first_doc.keys())}")

# 15. Inicia otro bucle 'for' que itera sobre cada par clave-valor (campo y su valor) dentro del first_doc.
        for field_name, field_value in first_doc.items():

# 16. Esta es la condición clave para detectar una posible clave foránea:
#     a) field_name.endswith("_id"): Verifica si el nombre del campo termina con "_id" (ej: "user_id").
#     b) field_name != "_id": Asegura que no estemos mirando el propio _id del documento.
#     c) isinstance(field_value, ObjectId): Verifica si el *valor* de ese campo es realmente un ObjectId. Esto hace más probable que sea una referencia a otro documento.
            if field_name.endswith("_id") and field_name != "_id" and isinstance(field_value, ObjectId):

# 17. Si la condición anterior es verdadera, imprime un mensaje indicando que se encontró un campo que parece una clave foránea.
                print(f"  > Campo encontrado '{field_name}' en '{source_collection_name}' que parece una clave foránea.")

# 18. Extrae el "nombre base" del campo quitando los últimos 3 caracteres ("_id"). Por ejemplo, de "user_id" obtiene "user".
                base_name = field_name[:-3]

# 19. Crea una lista de nombres potenciales para la colección a la que este campo podría estar refiriéndose. Se basa en convenciones comunes: el nombre base en singular y en plural. Ej: ["user", "users"].
                potential_target_names = [base_name, base_name + 's']

# 20. Inicializa una variable para guardar el nombre de la colección de destino si se encuentra. Se pone a None inicialmente.
                target_collection_name_found = None

# 21. Inicia un bucle 'for' para revisar cada nombre potencial de la colección destino (ej: "user", luego "users").
                for potential_target in potential_target_names:

# 22. Verifica si el nombre potencial (ej: "users") existe en la lista de nombres de colecciones reales que obtuvimos al principio.
                    if potential_target in collection_names:

# 23. Verifica que la colección encontrada no sea la misma colección de origen (evita relaciones reflexivas simples basadas en esta heurística, aunque podrían ser válidas).
                        if potential_target != source_collection_name:

# 24. Si se encuentra una colección válida que coincide, guarda su nombre en target_collection_name_found.
                            target_collection_name_found = potential_target

# 25. Imprime un mensaje indicando la posible colección referenciada.
                            print(f"     >> Posible referencia a la colección: '{target_collection_name_found}'")

# 26. Usa 'break' para salir del bucle de potential_target_names, ya que hemos encontrado una coincidencia.
                            break

# 27. Después de buscar en los nombres potenciales, verifica si se encontró un target_collection_name_found.
                if target_collection_name_found:

# 28. Si se encontró, crea una tupla que representa la relación. La tupla contiene:
#     a) Nombre de la colección de *destino* (la que tiene el _id original, ej: "users").
#     b) Nombre de la colección de *origen* (la que tiene la clave foránea, ej: "posts").
#     c) Cardinalidad: Asume "1:N" (Un usuario puede tener N posts). ¡Ojo! Esto es una suposición.
#     d) Nombre del campo de la clave foránea (ej: "user_id").
                    relation_tuple = (target_collection_name_found, source_collection_name, "1:N", field_name)

# 29. Verifica si esta tupla de relación *no* está ya en el conjunto detected_relationships.
                    if relation_tuple not in detected_relationships:

# 30. Si es una relación nueva, imprime un mensaje confirmando la detección y mostrando la relación de forma legible.
                        print(f"     ✅ Relación detectada: {relation_tuple[0]} --({relation_tuple[3]})--> {relation_tuple[1]} ({relation_tuple[2]})")

# 31. Añade la nueva tupla de relación al conjunto.
                        detected_relationships.add(relation_tuple)

# 32. Si la relación ya estaba en el conjunto (detectada quizás por otro documento de la misma colección)...
                    else:
# 33. Imprime un mensaje indicando que ya se había detectado.
                        print(f"     -> Relación {relation_tuple} ya detectada previamente.")

# 34. Si después de verificar los nombres potenciales *no* se encontró una colección de destino...
                else:
# 35. Imprime una advertencia indicando que no se pudo encontrar una colección correspondiente para ese campo _id, mostrando qué nombres se buscaron.
                    print(f"     ⚠️ No se encontró una colección correspondiente para '{field_name}' (se buscaron: {potential_target_names})")

# 36. Imprime un mensaje indicando que la detección ha terminado.
    print("--- Detección de relaciones finalizada ---")

# 37. Convierte el conjunto de relaciones detectadas a una lista y la devuelve como resultado de la función.
    return list(detected_relationships)


# 38. Genera un número entero aleatorio entre 1 y 1000 (ambos incluidos) y lo guarda en la variable 'x'.
x = random.randint(1, 1000)

# 39. Define la función principal que generará el gráfico ERD. Acepta db_data (los datos) y un nombre de archivo de salida opcional.
#     Si no se proporciona output_filename, usa un nombre por defecto que incluye el número aleatorio 'x' generado antes, para evitar sobreescribir archivos.
def generate_erd_graphviz_with_data_types(db_data, output_filename="Graph " + str(x) + " .png"):

# 40. Inicia un bloque try...except. Esto es crucial porque la generación de gráficos puede fallar por muchas razones (Graphviz no instalado, errores en pydot, etc.).
    try:
# 41. Crea un objeto de gráfico dirigido ('digraph') usando pydot.
#     - graph_type='digraph': Significa que las relaciones tendrán dirección (flechas).
#     - rankdir='LR': Sugiere a Graphviz que intente organizar el gráfico de Izquierda a Derecha (Left to Right).
        graph = pydot.Dot(graph_type='digraph', rankdir='LR')

# 42. Define una lista de colores en formato de texto. Se usarán para colorear los nodos (tablas/colecciones) en el gráfico.
        colors = ["lightblue", "lightgreen", "lightyellow", "lightcoral", "lightcyan", "lightsalmon", "lightpink", "lightgrey"]

# 43. Imprime un mensaje indicando que se van a crear los nodos (representaciones de las colecciones).
        print("\n--- Creando nodos para las colecciones ---")

# 44. Inicializa un índice para llevar la cuenta de qué color usar.
        color_index = 0

# 45. Inicia un bucle 'for' para iterar sobre cada colección en db_data.
        for collection_name, collection_data in db_data.items():

# 46. Selecciona un color de la lista 'colors'. Usa el operador módulo (%) para ciclar a través de los colores si hay más colecciones que colores en la lista.
            node_color = colors[color_index % len(colors)]

# 47. Incrementa el índice de color para la próxima iteración.
            color_index += 1

# 48. Empieza a construir la etiqueta (el texto que aparecerá dentro del nodo). Comienza con el nombre de la colección, una nueva línea, y una línea de guiones (-) del mismo largo que el nombre como separador visual.
            node_label = f"{collection_name}\n{'-'*len(collection_name)}\n"

# 49. Verifica si la colección tiene datos (no está vacía).
            if collection_data:
# 50. Si tiene datos, toma el primer documento (igual que en detect_relationships) para extraer los nombres y tipos de los campos.
                first_doc = collection_data[0]
# 51. Inicializa una lista vacía para guardar las cadenas "atributo: tipo".
                attribute_types = []
# 52. Itera sobre los campos (atributo, valor) del primer documento.
                for attr, value in first_doc.items():
# 53. Obtiene el nombre del tipo de dato del valor usando type(value).__name__. Ej: 'str', 'int', 'float', 'dict', 'list', 'ObjectId'.
                    data_type = type(value).__name__
# 54. Comprueba específicamente si el valor es un ObjectId.
                    if isinstance(value, ObjectId):
# 55. Si es ObjectId, sobrescribe data_type a "ObjectId" para que sea más legible que el nombre interno de la clase.
                        data_type = "ObjectId"
# 56. Comprueba si el valor es una lista.
                    elif isinstance(value, list):
# 57. Si es una lista, sobrescribe data_type a "list". (Podría mejorarse para mostrar el tipo dentro de la lista, pero este código no lo hace).
                        data_type = "list"
# 58. Añade la cadena formateada "nombre_del_campo: tipo_de_dato" a la lista attribute_types.
                    attribute_types.append(f"{attr}: {data_type}")
# 59. Une todas las cadenas de "atributo: tipo" con saltos de línea (\n) y las añade a la node_label que empezamos a construir antes.
                node_label += "\n".join(attribute_types)
# 60. Crea el objeto Nodo de pydot.
#     - collection_name: Es el identificador único del nodo dentro del grafo.
#     - label=node_label: Es el texto que se mostrará dentro del nodo (nombre, separador, atributos y tipos).
#     - shape='box': Define la forma del nodo como una caja rectangular.
#     - style="filled": Indica que el nodo debe rellenarse con color.
#     - fillcolor=node_color: Establece el color de relleno que seleccionamos antes.
                node = pydot.Node(collection_name, label=node_label, shape='box', style="filled", fillcolor=node_color)
# 61. Añade el nodo recién creado al objeto grafo.
                graph.add_node(node)
# 62. Imprime un mensaje confirmando la creación del nodo y cuántos atributos (campos) se listaron.
                print(f"Nodo creado para '{collection_name}' con {len(attribute_types)} atributos.")
# 63. Si la colección estaba vacía (el 'if collection_data:' fue falso)...
            else:
# 64. Añade "(Colección Vacía)" a la etiqueta del nodo.
                node_label += "(Colección Vacía)"
# 65. Crea el nodo para la colección vacía, similar al anterior pero añadiendo fontcolor="gray" para que el texto se vea gris y se distinga visualmente.
                node = pydot.Node(collection_name, label=node_label, shape='box', style="filled", fillcolor=node_color, fontcolor="gray")
# 66. Añade el nodo de la colección vacía al grafo.
                graph.add_node(node)
# 67. Imprime un mensaje indicando que se creó un nodo para una colección vacía.
                print(f"Nodo creado para colección vacía: '{collection_name}'.")
# 68. Imprime un mensaje separador indicando que la creación de nodos ha terminado.
        print("--- Nodos creados ---")

# 69. Llama a la función detect_relationships que definimos antes, pasándole los mismos db_data, para obtener la lista de relaciones detectadas.
        relationships = detect_relationships(db_data)

# 70. Imprime un mensaje indicando que se van a añadir las aristas (las flechas que representan las relaciones).
        print("\n--- Añadiendo aristas para las relaciones detectadas ---")

# 71. Verifica si la lista de relaciones está vacía.
        if not relationships:
# 72. Si no hay relaciones, imprime un mensaje indicándolo.
             print("No se detectaron relaciones automáticamente.")
# 73. Si sí hay relaciones...
        else:
# 74. Itera sobre cada tupla de relación en la lista relationships. Desempaqueta la tupla en las variables src, dest, cardinality, attribute.
#     ¡OJO! Recordar cómo se creó la tupla:
#     - src = target_collection_name_found (ej: "users", el lado "1" de la relación)
#     - dest = source_collection_name (ej: "posts", el lado "N" donde está la FK)
#     - cardinality = "1:N" (la cardinalidad asumida)
#     - attribute = field_name (ej: "user_id", el nombre de la FK)
            for src, dest, cardinality, attribute in relationships:
# 75. Comprueba si ambos nodos (el de origen 'src' y el de destino 'dest' de la arista) existen realmente en el grafo que hemos construido. Es una medida de seguridad.
                if graph.get_node(src) and graph.get_node(dest):
# 76. Si ambos nodos existen, crea un objeto Arista (Edge) de pydot.
#     - src: Nodo de origen de la flecha (ej: "users").
#     - dest: Nodo de destino de la flecha (ej: "posts").
#     - label=f"{cardinality}\n({attribute})": Etiqueta que se mostrará sobre la flecha, indicando la cardinalidad y el nombre del campo FK entre paréntesis.
                    edge = pydot.Edge(src, dest, label=f"{cardinality}\n({attribute})")
# 77. Añade la arista al grafo.
                    graph.add_edge(edge)
# 78. Imprime un mensaje confirmando que se añadió la arista.
                    print(f"Arista añadida: {src} -> {dest} [{attribute}]")
# 79. Si alguno de los nodos (o ambos) no se encontró en el grafo...
                else:
# 80. Imprime una advertencia indicando que no se pudo añadir la arista porque falta alguno de los nodos. Esto podría pasar si hubo algún error al crear los nodos o si la lógica de detección encontró algo inconsistente.
                     print(f"⚠️ Advertencia: Nodo '{src}' o '{dest}' no encontrado en el grafo. No se pudo añadir la arista para ({src}, {dest}, {attribute}).")
# 81. Imprime un mensaje separador indicando que se terminó de añadir aristas.
        print("--- Aristas añadidas ---")

# 82. Imprime un mensaje indicando que se va a intentar guardar el gráfico y muestra el nombre del archivo.
        print(f"\nIntentando guardar el gráfico en: {output_filename}")

# 83. ¡La magia de Graphviz! Llama al método write_png del objeto grafo. Este método:
#     a) Genera la descripción del grafo en formato DOT.
#     b) Invoca al programa 'dot' de Graphviz (que debe estar instalado y accesible en el PATH del sistema).
#     c) Le pasa la descripción DOT al programa 'dot'.
#     d) El programa 'dot' calcula la disposición de nodos y aristas y renderiza el gráfico como una imagen PNG.
#     e) Guarda la imagen PNG en el archivo especificado por output_filename.
        graph.write_png(output_filename)

# 84. Si todo fue bien hasta aquí, imprime un mensaje de éxito confirmando dónde se guardó el archivo.
        print(f"✅ Diagrama ERD con detección automática de relaciones guardado exitosamente en: {output_filename}")

# 85. Empieza la sección de manejo de errores (bloque 'except'). Este bloque captura específicamente el error ImportError.
    except ImportError as ie:
# 86. Si ocurre un ImportError (normalmente porque 'pydot' no está instalado, o peor, porque 'pydot' no puede encontrar Graphviz), imprime un mensaje de error claro.
        print(f"\n❌ ERROR DE IMPORTACIÓN: {ie}")
# 87. Da una pista sobre la causa probable: pydot o Graphviz no están instalados/configurados.
        print("Parece que 'pydot' o su dependencia 'Graphviz' no están instalados o configurados correctamente.")
# 88. Indica cómo instalar pydot.
        print("Para instalar pydot, usa: pip install pydot")
# 89. Advierte que Graphviz también debe estar instalado A NIVEL DEL SISTEMA OPERATIVO y su carpeta 'bin' debe estar en la variable de entorno PATH. Esto es crucial y una fuente común de errores.
        print("Graphviz también debe estar instalado en tu sistema Y en el PATH.")
# 90. Proporciona la URL de descarga de Graphviz.
        print("Descarga Graphviz desde: https://graphviz.org/download/")
# 91. Reitera la importancia de añadir la carpeta 'bin' de Graphviz al PATH.
        print("Asegúrate de añadir la carpeta 'bin' de Graphviz a la variable de entorno PATH.")

# 92. Este bloque captura cualquier otra excepción genérica que no sea ImportError.
    except Exception as e:
# 93. Imprime un mensaje de error genérico indicando que algo inesperado ocurrió. Muestra el mensaje de la excepción (e).
        print(f"\n❌ Ocurrió un error inesperado durante la generación del gráfico: {e}")
# 94. Imprime un encabezado para el traceback detallado.
        print("\n--- Traceback detallado ---")
# 95. Usa la librería traceback para imprimir la pila de llamadas completa del error. Esto es súper útil para diagnosticar qué falló y dónde.
        traceback.print_exc()
# 96. Imprime un pie de página para el traceback.
        print("--------------------------")


# --- Creación de Datos de Ejemplo ---
# 97-119: Crean instancias de ObjectId. Esto simula los _id únicos que MongoDB asignaría a cada documento si estos datos estuvieran en una base de datos real. Guardar estos IDs en variables permite luego usarlos para crear las referencias (claves foráneas) en los datos de ejemplo.
user1_id = ObjectId()
user2_id = ObjectId()
user3_id = ObjectId()
post1_id = ObjectId()
post2_id = ObjectId()
post3_id = ObjectId()
comment1_id = ObjectId()
comment2_id = ObjectId()
comment3_id = ObjectId()
category1_id = ObjectId()
category2_id = ObjectId()
tag1_id = ObjectId()
tag2_id = ObjectId()
tag3_id = ObjectId()
product1_id = ObjectId()
product2_id = ObjectId()
review1_id = ObjectId()
review2_id = ObjectId()
review3_id = ObjectId()
tagging1_id = ObjectId()
tagging2_id = ObjectId()
tagging3_id = ObjectId()
tagging4_id = ObjectId()

# 120: Define la variable db_data. Es un diccionario que simula una pequeña base de datos NoSQL (como MongoDB).
db_data = {
# 121: Clave "users": representa la colección de usuarios. El valor es una lista de diccionarios.
    "users": [
# 122-124: Cada diccionario representa un documento de usuario, con un _id (usando los ObjectId creados antes) y otros campos.
        {"_id": user1_id, "name": "Alice", "city": "Metropolis"},
        {"_id": user2_id, "name": "Bob", "city": "Gotham"},
        {"_id": user3_id, "name": "Charlie", "city": "Star City"}
    ],
# 125: Clave "categories": colección de categorías.
    "categories": [
        {"_id": category1_id, "name": "Tutorials", "type": "blog"},
        {"_id": category2_id, "name": "Electronics", "type": "store"}
    ],
# 128: Clave "posts": colección de publicaciones de blog.
    "posts": [
# 129-131: Documentos de post. Fíjate cómo usan user_id y category_id con los ObjectId correspondientes para crear las *relaciones* con las colecciones "users" y "categories". Estos son los campos que detect_relationships buscará.
        {"_id": post1_id, "title": "Advanced Python", "content": "...", "user_id": user1_id, "category_id": category1_id},
        {"_id": post2_id, "title": "Intro to MongoDB", "content": "...", "user_id": user2_id, "category_id": category1_id},
        {"_id": post3_id, "title": "Data Viz", "content": "...", "user_id": user1_id, "category_id": category1_id}
    ],
# 132: Clave "comments": colección de comentarios.
    "comments": [
# 133-135: Documentos de comentario, relacionados con "posts" (a través de post_id) y "users" (a través de user_id).
        {"_id": comment1_id, "text": "Very helpful!", "post_id": post1_id, "user_id": user2_id},
        {"_id": comment2_id, "text": "Good explanation.", "post_id": post2_id, "user_id": user1_id},
        {"_id": comment3_id, "text": "I have a question...", "post_id": post1_id, "user_id": user3_id}
    ],
# 136: Clave "products": colección de productos de una tienda.
    "products": [
# 137-138: Documentos de producto, relacionados con "users" (usando seller_id como FK) y "categories". Nota el cambio de nombre de "user_id" a "seller_id", la lógica de detección lo encontrará igual porque termina en "_id".
        {"_id": product1_id, "name": "Laptop Pro", "price": 1200.00, "seller_id": user1_id, "category_id": category2_id},
        {"_id": product2_id, "name": "Wireless Mouse", "price": 25.50, "seller_id": user2_id, "category_id": category2_id}
    ],
# 139: Clave "reviews": colección de reseñas de productos.
    "reviews": [
# 140-142: Documentos de reseña, relacionados con "products" y "users".
        {"_id": review1_id, "text": "Excellent product!", "rating": 5, "product_id": product1_id, "user_id": user2_id},
        {"_id": review2_id, "text": "Works great.", "rating": 4, "product_id": product2_id, "user_id": user3_id},
        {"_id": review3_id, "text": "Good value for money.", "rating": 4, "product_id": product1_id, "user_id": user3_id}
    ],
# 143: Clave "tags": colección de etiquetas (tags).
    "tags": [
        {"_id": tag1_id, "name": "python"},
        {"_id": tag2_id, "name": "database"},
        {"_id": tag3_id, "name": "webdev"}
    ],
# 147: Clave "taggings": Esta es una colección de *asociación* (o tabla intermedia en SQL). Se usa para implementar una relación Muchos-a-Muchos (N:M) entre "posts" y "tags". Un post puede tener muchas tags, y una tag puede estar en muchos posts.
    "taggings": [
# 148-151: Cada documento aquí vincula un post_id con un tag_id. detect_relationships identificará dos relaciones 1:N aquí: tags -> taggings y posts -> taggings. El gráfico resultante mostrará estas dos relaciones.
        {"_id": tagging1_id, "post_id": post1_id, "tag_id": tag1_id},
        {"_id": tagging2_id, "post_id": post2_id, "tag_id": tag2_id},
        {"_id": tagging3_id, "post_id": post1_id, "tag_id": tag3_id},
        {"_id": tagging4_id, "post_id": post3_id, "tag_id": tag1_id}
    ]
# 152: Cierra la definición del diccionario db_data.
}

# 154: Llama a la función principal generate_erd_graphviz_with_data_types, pasándole el diccionario db_data que acabamos de definir. Esto inicia todo el proceso: crear nodos, detectar relaciones, añadir aristas y guardar el archivo PNG del gráfico ERD.
generate_erd_graphviz_with_data_types(db_data)