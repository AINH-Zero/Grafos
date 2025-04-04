import pydot
from bson.objectid import ObjectId
import random

def generate_erd_graphviz_with_data_types(db_data, output_filename="erd_mongodb_datatypes.png"):
    """
    Genera un Diagrama Entidad-Relación (ERD) con atributos y tipos de datos para los nodos.
    """
    try:
        graph = pydot.Dot(graph_type='digraph', rankdir='LR')  # LR para disposición de izquierda a derecha
        colors = ["lightblue", "lightgreen", "lightyellow", "lightcoral", "lightcyan", "lightsalmon"]  # Paleta de colores

        # Agregar nodos (entidades) con atributos y tipos de datos
        for collection_name, collection_data in db_data.items():
            if collection_data:  # Verificar si la colección tiene documentos
                first_doc = collection_data[0]
                attribute_types = []
                for attr, value in first_doc.items():
                    data_type = type(value).__name__  # Obtener el nombre del tipo de dato
                    attribute_types.append(f"{attr}: {data_type}")
                node_label = f"{collection_name}\n" + "\n".join(attribute_types)
                node = pydot.Node(collection_name, label=node_label, shape='box', style="filled", fillcolor=random.choice(colors))  # Asignar un color aleatorio
                graph.add_node(node)
            else:
                # Manejar el caso de colecciones vacías
                node = pydot.Node(collection_name, label=f"{collection_name}\n(Sin datos)", shape='box', style="filled", fillcolor=random.choice(colors))
                graph.add_node(node)

        # Definir relaciones y atributos de relación (sin cambios)
        relationships = [
            ("users", "posts", "1:N", "user_id"),
            ("users", "comments", "1:N", "user_id"),
            ("posts", "comments", "1:N", "post_id")
        ]

        # Agregar aristas (relaciones) con etiquetas (sin cambios)
        for src, dest, cardinality, attribute in relationships:
            edge = pydot.Edge(src, dest, label=f"{cardinality}\n({attribute})")
            graph.add_edge(edge)

        # Guardar el gráfico en un archivo (sin cambios)
        graph.write_png(output_filename)

        print(f"Diagrama ERD con atributos y tipos de datos guardado en: {output_filename}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Simulación de Datos Genéricos en Memoria (sin cambios)
user1_id = ObjectId()
user2_id = ObjectId()
post1_id = ObjectId()
post2_id = ObjectId()
post3_id = ObjectId()
comment1_id = ObjectId()
comment2_id = ObjectId()
comment3_id = ObjectId()

db_data = {
    "users": [
        {"_id": user1_id, "name": "Alice"},
        {"_id": user2_id, "name": "Bob"}
    ],
    "posts": [
        {"_id": post1_id, "title": "Python Basics", "user_id": user1_id},
        {"_id": post2_id, "title": "MongoDB Guide", "user_id": user2_id},
        {"_id": post3_id, "title": "Another Post", "user_id": user1_id}
    ],
    "comments": [
        {"_id": comment1_id, "text": "Great post!", "post_id": post1_id, "user_id": user2_id},
        {"_id": comment2_id, "text": "Useful info.", "post_id": post2_id, "user_id": user1_id},
        {"_id": comment3_id, "text": "nice comment", "post_ponte_id": post1_id, "user_id": user1_id}
    ]
}

generate_erd_graphviz_with_data_types(db_data)